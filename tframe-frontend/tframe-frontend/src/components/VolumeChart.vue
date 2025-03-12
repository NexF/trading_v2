<template>
    <div ref="volumeChartContainer" class="volume-chart"></div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, onUnmounted, watch } from 'vue'
  import type { 
    IChartApi, 
    DeepPartial, 
    ChartOptions, 
    HistogramSeriesOptions,
    Time,
    Range
  } from 'lightweight-charts'
  import { createChart } from 'lightweight-charts'
  import type { VolumeData } from '../utils/chartUtils'
  
  // 定义组件接收的属性
  const props = defineProps<{
    // 成交量数据数组
    data: VolumeData[]
    // 可视区域的时间范围
    timeRange?: {
      from: number
      to: number
    }
    // 十字光标位置信息
    crosshairPosition?: {
      x: number       // 光标X坐标
      y: number       // 光标Y坐标
      prices: Map<any, number>  // 当前光标位置的价格信息
    }
  }>()
  
  // 定义组件可以触发的事件
  const emit = defineEmits<{
    (e: 'timeRangeChanged', range: { from: number, to: number }): void
  }>()
  
  const volumeChartContainer = ref<HTMLElement | null>(null)
  let chart: IChartApi | null = null
  let volumeSeries: any = null
  
  // 创建成交量图配置
  const createChartOptions = (container: HTMLElement): DeepPartial<ChartOptions> => ({
    width: container.clientWidth,
    height: 150,
    layout: {
      background: { color: '#ffffff' },
      textColor: '#333',
    },
    grid: {
      vertLines: { color: '#f0f0f0' },
      horzLines: { color: '#f0f0f0' },
    },
    rightPriceScale: {
      borderColor: '#dfdfdf',
    },
    timeScale: {
      visible: false, // 隐藏时间轴，使用主图的时间轴
    },
  })
  
  // 初始化图表
  const initChart = () => {
    if (!volumeChartContainer.value) return
  
    // 创建成交量图表实例
    chart = createChart(volumeChartContainer.value, createChartOptions(volumeChartContainer.value))
    
    // 添加成交量柱状图系列
    volumeSeries = chart.addHistogramSeries({
      color: '#26a69a',
      priceFormat: {
        type: 'volume',  // 设置为成交量格式
      },
    })
  
    // 设置初始数据
    volumeSeries.setData(props.data)
    
    // 监听时间轴的可视范围变化
    // 当用户缩放或平移图表时，这个事件会被触发
    chart.timeScale().subscribeVisibleTimeRangeChange((timeRange) => {
      // 向父组件发送时间范围变化事件，用于同步主图的时间范围
      if (timeRange) {
        emit('timeRangeChanged', {
          from: timeRange.from as number,
          to: timeRange.to as number
        })
      }
    })
  }
  
  // 处理窗口大小变化
  const handleResize = () => {
    if (volumeChartContainer.value && chart) {
      const width = volumeChartContainer.value.clientWidth
      chart.applyOptions({ width })
    }
  }
  
  // 监听属性变化
  watch(() => props.timeRange, (newRange) => {
    if (chart && newRange) {
      chart.timeScale().setVisibleRange({
        from: newRange.from as Time,
        to: newRange.to as Time
      })
    }
  }, { deep: true })
  
  watch(() => props.crosshairPosition, (newPosition) => {
    // Remove crosshair position setting for volume chart
    // Volume chart should follow main chart's crosshair, not set its own
    console.log('Crosshair position updated:', newPosition)
  }, { deep: true })
  
  watch(() => props.data, (newData) => {
    if (volumeSeries) {
      volumeSeries.setData(newData)
    }
  }, { deep: true })
  
  // 生命周期钩子
  onMounted(() => {
    initChart()
    window.addEventListener('resize', handleResize)
  })
  
  onUnmounted(() => {
    if (chart) chart.remove()
    window.removeEventListener('resize', handleResize)
  })
  </script>
  
  <style scoped>
  .volume-chart {
    width: 100%;
    height: 150px;
  }
  </style>