<script setup lang="ts">
// 所有导入语句必须在顶部
import { createChart, ColorType, CrosshairMode } from 'lightweight-charts'
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import { useDark } from '@vueuse/core'
import VolumeChart from './VolumeChart.vue'
import { 
  fetchKlineData, 
  transformKlineData, 
  transformVolumeData, 
  addChartTools,
} from '../utils/chartUtils'
import type { 
  KlineData, 
  ChartData, 
  VolumeData 
} from '../utils/chartUtils'

const isDark = useDark()
const mainChartContainer = ref<HTMLElement | null>(null)
let mainChart: any = null
let candleSeries: any = null

// 响应式状态管理
const state = reactive({
  klineData: [] as KlineData[],
  chartData: [] as ChartData[],
  loading: false,
  error: null as string | null
})

// 用于同步的数据
const timeRange = ref<{from: number, to: number} | undefined>(undefined)
const crosshairPosition = ref<{
  x: number, 
  y: number, 
  prices: Map<any, number>
} | undefined>(undefined)
const volumeData = ref<VolumeData[]>([])

// 获取 K 线数据的方法
const loadKlineData = async () => {
  state.loading = true
  state.error = null

  try {
    // 获取 K 线数据
    state.klineData = await fetchKlineData()
    
    // 转换数据格式
    state.chartData = transformKlineData(state.klineData)
    volumeData.value = transformVolumeData(state.klineData)

    // 设置 K 线数据
    if (candleSeries) {
      candleSeries.setData(state.chartData)
    }

  } catch (error) {
    console.error('Failed to fetch K-line data:', error)
    state.error = '无法获取 K 线数据'
  } finally {
    state.loading = false
  }
}

// 初始化图表函数
const initMainChart = () => {
  console.log('Init chart called')
  if (!mainChartContainer.value) {
    console.error('Chart container not found')
    return
  }

  try {
    const chartOptions = {
      width: mainChartContainer.value.clientWidth,
      height: 400,
      layout: {
        background: { color: isDark.value ? '#1a1a1a' : '#ffffff' },
        textColor: isDark.value ? '#ffffff' : '#333',
      },
      grid: {
        vertLines: { color: isDark.value ? '#333' : '#f0f0f0' },
        horzLines: { color: isDark.value ? '#333' : '#f0f0f0' },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
      },
      rightPriceScale: {
        borderColor: '#dfdfdf',
      },
      timeScale: {
        borderColor: '#dfdfdf',
        timeVisible: true,
        secondsVisible: false,
      },
    }

    // 创建图表实例
    mainChart = createChart(mainChartContainer.value, chartOptions)

    // 创建 K 线系列
    candleSeries = mainChart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderUpColor: '#26a69a',
      borderDownColor: '#ef5350',
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    })

    // 同步时间轴
    mainChart.timeScale().subscribeVisibleTimeRangeChange((range: {from: number, to: number}) => {
      timeRange.value = range
    })

    // 同步十字光标
    mainChart.subscribeCrosshairMove((param: any) => {
      crosshairPosition.value = param.point ? {
        x: param.point.x,
        y: param.point.y,
        prices: param.seriesPrices
      } : undefined
    })

    // 添加MA线等技术指标
    addChartTools(mainChart, candleSeries)

    // 自适应大小
    window.addEventListener('resize', handleResize)

    // 获取 K 线数据
    loadKlineData()

    console.log('Chart setup completed')
  } catch (error) {
    console.error('Chart initialization error:', error)
  }
}

// 处理窗口大小变化
const handleResize = () => {
  if (mainChart && mainChartContainer.value) {
    mainChart.applyOptions({
      width: mainChartContainer.value.clientWidth,
    })
  }
}

// 处理成交量图时间范围变化
const handleVolumeTimeRangeChange = (range: {from: number, to: number}) => {
  if (mainChart && range) {
    mainChart.timeScale().setVisibleRange(range)
  }
}

// 生命周期钩子
onMounted(() => {
  console.log('Component mounted')
  setTimeout(initMainChart, 100)
})

onUnmounted(() => {
  if (mainChart) {
    mainChart.remove()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <div class="trading-view-container">
    <div v-if="state.loading" class="loading">
      加载中...
    </div>
    <div v-else-if="state.error" class="error">
      {{ state.error }}
    </div>
    <div v-else>
      <div ref="mainChartContainer" class="main-chart"></div>
      <VolumeChart 
        :data="volumeData"           
        :timeRange="timeRange"       
        :crosshairPosition="crosshairPosition"  
        @timeRangeChanged="handleVolumeTimeRangeChange"  
      />
    </div>
  </div>
</template>

<style scoped>
.trading-view-container {
  width: 100%;
  padding: 20px;
  background-color: var(--el-bg-color);
  border-radius: 8px;
}

.main-chart {
  width: 100%;
  height: 400px;
  margin-bottom: 8px;
}

.loading, .error {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
  color: #666;
}
</style>