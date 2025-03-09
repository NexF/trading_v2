<script setup lang="ts">
// 所有导入语句必须在顶部
import { createChart, ColorType, CrosshairMode } from 'lightweight-charts'
import { ref, onMounted, onUnmounted } from 'vue'
import { useDark } from '@vueuse/core'
import VolumeChart from './VolumeChart.vue'
import { generateDemoData, addChartTools } from '../utils/chartUtils'

// 在这里进行其他初始化和错误处理
console.log('Testing imports...')

const isDark = useDark()
const mainChartContainer = ref<HTMLElement | null>(null)
let mainChart: any = null
let candleSeries: any = null

// 用于同步的数据
const timeRange = ref(null)
const crosshairPosition = ref(null)
const volumeData = ref([])

// 3. 简化初始化函数，先测试基本功能
const initMainChart = () => {
  console.log('Init chart called')
  if (!mainChartContainer.value) {
    console.error('Chart container not found')
    return
  }

  try {
    console.log('Creating chart...')
    const chartOptions = {
      width: mainChartContainer.value.clientWidth,
      height: 400,
      layout: {
        background: { color: '#ffffff' },
        textColor: '#333',
      },
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
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
    console.log('Chart instance created:', mainChart)

    // 创建 K 线系列
    candleSeries = mainChart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderUpColor: '#26a69a',
      borderDownColor: '#ef5350',
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    })
    console.log('Candlestick series created:', candleSeries)

    // 同步时间轴
    mainChart.timeScale().subscribeVisibleTimeRangeChange((range) => {
      timeRange.value = range
    })

    // 同步十字光标
    mainChart.subscribeCrosshairMove((param) => {
      crosshairPosition.value = {
        x: param.point?.x,
        y: param.point?.y,
        prices: param.seriesPrices,
      }
    })

    // 设置数据
    const data = generateDemoData()
    candleSeries.setData(data.klineData)
    volumeData.value = data.volumeData

    // 添加MA线等技术指标
    addChartTools(mainChart, candleSeries)

    // 自适应大小
    window.addEventListener('resize', handleResize)

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

/**
 * 处理成交量图时间范围变化的函数
 * 当用户在成交量图上进行缩放或平移操作时，
 * 这个函数会被调用来同步主图的时间范围
 * @param range - 新的时间范围对象 {from: number, to: number}
 */
const handleVolumeTimeRangeChange = (range) => {
  // 确保主图存在且收到有效的时间范围
  if (mainChart && range) {
    // 设置主图的可视时间范围，实现两个图表的同步
    mainChart.timeScale().setVisibleRange(range)
  }
}

// 4. 简化生命周期钩子
onMounted(() => {
  console.log('Component mounted')
  // 给 DOM 一点时间来渲染
  setTimeout(() => {
    initMainChart()
  }, 100)
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
    <div ref="mainChartContainer" class="main-chart"></div>
    <!-- 成交量图表组件 -->
    <VolumeChart 
      :data="volumeData"           
      :timeRange="timeRange"       
      :crosshairPosition="crosshairPosition"  
      @timeRangeChanged="handleVolumeTimeRangeChange"  
    />
    <!-- 
      :data - 传递成交量数据
      :timeRange - 传递时间范围
      :crosshairPosition - 传递十字光标位置
      @timeRangeChanged - 监听时间范围变化事件
    -->
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
</style>