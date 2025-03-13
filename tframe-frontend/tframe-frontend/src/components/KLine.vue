<script setup lang="ts">
// 所有导入语句必须在顶部
import { createChart, ColorType, CrosshairMode } from 'lightweight-charts'
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import { timestamp, useDark } from '@vueuse/core'
import VolumeChart from './VolumeChart.vue'
import { fetchKlineData } from '../api/klineApi'
import { 
  transformKlineData, 
  transformVolumeData, 
  addChartTools,
  generateDemoData
} from '../utils/chartUtils'
import type { 
  ChartData, 
  VolumeData 
} from '../utils/chartUtils'
import type { KlineData } from '../api/klineApi'

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
  console.log('Starting loadKlineData function...', new Date().toISOString());
  state.loading = true;
  state.error = null;

  try {
    // 确保candleSeries已初始化
    if (!candleSeries) {
      console.error('candleSeries is not initialized, cannot load data');
      state.error = '图表未初始化';
      return;
    }

    let chartData = [];
    let volumeChartData = [];

    try {
      console.log('Fetching data from API...', new Date().toISOString());
      
      // 先使用演示数据快速渲染图表
      const demoData = generateDemoData();
      chartData = demoData.klineData;
      volumeChartData = demoData.volumeData;
      
      // 更新状态
      state.chartData = chartData;
      volumeData.value = volumeChartData;
      
      // 立即渲染演示数据
      updateChart(chartData);
      
      // 然后异步加载真实数据
      console.log('Pre-rendered with demo data, now fetching real data...');
      fetchKlineData().then(realData => {
        if (realData && realData.length > 0) {
          console.log('API data received:', realData.length, 'items', new Date().toISOString());
          const realChartData = transformKlineData(realData);
          const realVolumeData = transformVolumeData(realData);
          
          // 更新状态
          state.chartData = realChartData;
          volumeData.value = realVolumeData;
          
          // 更新图表
          updateChart(realChartData);
          console.log('Chart updated with real data');
        }
      }).catch(err => {
        console.warn('Failed to fetch real data, keeping demo data:', err);
      });
      
    } catch (apiError) {
      console.warn('Using demo data due to API error:', apiError);
      const demoData = generateDemoData();
      chartData = demoData.klineData;
      volumeChartData = demoData.volumeData;
      
      // 更新状态
      state.chartData = chartData;
      volumeData.value = volumeChartData;
      
      // 渲染演示数据
      updateChart(chartData);
      console.log('Using demo data:', chartData.length, 'items');
    }
    
    console.log('loadKlineData initial rendering completed', new Date().toISOString());
  } catch (error: any) { // 显式类型标注解决linter错误
    console.error('Error in loadKlineData:', error);
    state.error = '加载数据失败: ' + (error.message || '未知错误');
  } finally {
    state.loading = false;
  }
}

// 更新图表的辅助函数
const updateChart = (chartData: ChartData[]) => {
  if (!candleSeries || !mainChart) {
    console.error('Chart not initialized');
    return;
  }
  
  console.log('Updating chart with', chartData.length, 'items');
  
  // 格式化数据
  const formattedData = chartData.map(item => {
    let timeValue = Math.floor(Number(item.time));
    return {
      time: timeValue,
      open: Number(item.open),
      high: Number(item.high),
      low: Number(item.low),
      close: Number(item.close)
    };
  });

  // 设置数据到图表
  candleSeries.setData(formattedData);
  
  // 调整可视区域以显示所有数据
  mainChart.timeScale().fitContent();
  
  // 添加技术指标
  setTimeout(() => {
    try {
      addChartTools(mainChart, candleSeries);
    } catch (error) {
      console.warn('Failed to add chart tools:', error);
    }
  }, 200);
}

// 初始化图表函数
const initMainChart = () => {
  if (!mainChartContainer.value) {
    console.error('Chart container not found')
    return
  }

  try {
    // 确保容器有正确的尺寸
    if (mainChartContainer.value) {
      mainChartContainer.value.style.width = '100%'
      mainChartContainer.value.style.height = '400px'
    }
    
    // 创建图表配置
    const chartOptions = {
      width: mainChartContainer.value.clientWidth || 800,
      height: 400,
      layout: {
        background: { type: ColorType.Solid, color: '#ffffff' },
        textColor: '#333333',
        fontSize: 12,
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
        visible: true,
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
      if (range && range.from !== null && range.to !== null) {
        timeRange.value = range
      }
    })

    // 同步十字光标
    mainChart.subscribeCrosshairMove((param: any) => {
      crosshairPosition.value = param.point ? {
        x: param.point.x,
        y: param.point.y,
        prices: param.seriesPrices
      } : undefined
    })

    // 自适应大小
    window.addEventListener('resize', handleResize)
    
    // 立即加载数据
    loadKlineData()
    console.log('Loading K-line data...', new Date().toISOString());
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
  if (!mainChart || !range || range.from === null || range.to === null) {
    console.log('Invalid range or chart not initialized:', range);
    return;
  }
  
  try {
    mainChart.timeScale().setVisibleRange({
      from: range.from,
      to: range.to
    });
  } catch (error) {
    console.error('Error setting visible range:', error);
  }
}

// 生命周期钩子
onMounted(() => {
  console.log('Component mounted, waiting for DOM to render...');
  // 确保DOM已完全渲染
  setTimeout(() => {
    console.log('Initializing main chart...');
    initMainChart();
  }, 100);
})

onUnmounted(() => {
  console.log('Component unmounting, cleaning up...');
  if (mainChart) {
    try {
      mainChart.remove();
      console.log('Chart removed successfully');
    } catch (error) {
      console.error('Error removing chart:', error);
    }
  }
  window.removeEventListener('resize', handleResize);
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
    <div v-else class="charts-container">
      <div ref="mainChartContainer" class="main-chart"></div>
      <div class="volume-container">
        <VolumeChart 
          :data="volumeData"           
          :timeRange="timeRange"       
          :crosshairPosition="crosshairPosition"  
          @timeRangeChanged="(range) => handleVolumeTimeRangeChange(range)"  
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.trading-view-container {
  width: 100%;
  padding: 20px;
  background-color: #ffffff;
  border-radius: 8px;
  overflow: hidden;
}

.charts-container {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.main-chart {
  width: 100%;
  height: 400px;
  margin-bottom: 8px;
  position: relative;
  border: 1px solid #ddd;
  background-color: #fff;
  z-index: 1;
}

.volume-container {
  width: 100%;
  height: 150px;
  position: relative;
  border: 1px solid #ddd;
}

.loading, .error {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
  color: #666;
}
</style>