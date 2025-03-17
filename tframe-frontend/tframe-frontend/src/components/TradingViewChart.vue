<template>
  <div class="trading-view-chart-container">
    <div ref="chartContainer" class="chart-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { createChart, ColorType, CrosshairMode } from 'lightweight-charts';
import type { Time, UTCTimestamp } from 'lightweight-charts';
import type { KlineData } from '../api/klineApi';

// 定义组件的props
interface Props {
  data: KlineData[];
  title?: string;
  colors?: {
    backgroundColor?: string;
    lineColor?: string;
    textColor?: string;
    areaTopColor?: string;
    areaBottomColor?: string;
    upColor?: string;
    downColor?: string;
    borderUpColor?: string;
    borderDownColor?: string;
    wickUpColor?: string;
    wickDownColor?: string;
  };
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  colors: () => ({
    backgroundColor: 'white',
    lineColor: '#2962FF',
    textColor: 'black',
    areaTopColor: 'rgba(41, 98, 255, 0.3)',
    areaBottomColor: 'rgba(41, 98, 255, 0.0)',
    upColor: '#26a69a',
    downColor: '#ef5350',
    borderUpColor: '#26a69a',
    borderDownColor: '#ef5350',
    wickUpColor: '#26a69a',
    wickDownColor: '#ef5350'
  })
});

// 声明chart引用和容器引用
const chartContainer = ref<HTMLElement | null>(null);
let chart: any = null;
let candleSeries: any = null;
let volumeSeries: any = null;

// 将K线数据转换为图表库可接受的格式
const formatCandleData = (data: KlineData[]) => {
  return data.map(item => {
    // 解析日期时间，格式为 "20250303 09:30:00"
    const timestamp = item.timestamp || item.date;
    const dateStr = timestamp.replace(/\s+/g, 'T') + 'Z';
    const time = new Date(dateStr).getTime() / 1000 as UTCTimestamp;
    
    return {
      time,
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close
    };
  });
};

// 将交易量数据转换为图表库可接受的格式
const formatVolumeData = (data: KlineData[]) => {
  return data.map(item => {
    // 解析日期时间
    const timestamp = item.timestamp || item.date;
    const dateStr = timestamp.replace(/\s+/g, 'T') + 'Z';
    const time = new Date(dateStr).getTime() / 1000 as UTCTimestamp;
    
    const color = item.close >= item.open 
      ? props.colors.upColor 
      : props.colors.downColor;
    
    return {
      time,
      value: item.volume,
      color
    };
  });
};

// 初始化图表
const initChart = () => {
  if (chartContainer.value) {
    // 创建图表
    chart = createChart(chartContainer.value, {
      width: chartContainer.value.clientWidth,
      height: chartContainer.value.clientHeight,
      layout: {
        background: { type: ColorType.Solid, color: props.colors.backgroundColor },
        textColor: props.colors.textColor,
      },
      grid: {
        vertLines: { color: 'rgba(42, 46, 57, 0.1)' },
        horzLines: { color: 'rgba(42, 46, 57, 0.1)' },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
      },
      timeScale: {
        timeVisible: true,
        borderColor: 'rgba(197, 203, 206, 0.8)',
      },
      rightPriceScale: {
        borderColor: 'rgba(197, 203, 206, 0.8)',
      }
    });

    // 创建K线图序列
    candleSeries = chart.addCandlestickSeries({
      upColor: props.colors.upColor,
      downColor: props.colors.downColor,
      borderUpColor: props.colors.borderUpColor,
      borderDownColor: props.colors.borderDownColor,
      wickUpColor: props.colors.wickUpColor,
      wickDownColor: props.colors.wickDownColor,
    });

    // 创建交易量序列
    volumeSeries = chart.addHistogramSeries({
      color: '#26a69a',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '', // 将交易量放在单独的价格轴上
    });

    // 适应窗口大小的处理函数
    const handleResize = () => {
      if (chart && chartContainer.value) {
        chart.applyOptions({
          width: chartContainer.value.clientWidth,
          height: chartContainer.value.clientHeight,
        });
      }
    };

    // 添加窗口大小变化的监听器
    window.addEventListener('resize', handleResize);

    // 数据更新时重新渲染
    if (props.data && props.data.length > 0) {
      updateChartData();
    }

    // 返回清理函数，用于移除事件监听器
    onUnmounted(() => {
      window.removeEventListener('resize', handleResize);
      if (chart) {
        chart.remove();
        chart = null;
      }
    });
  }
};

// 更新图表数据
const updateChartData = () => {
  if (candleSeries && volumeSeries && props.data && props.data.length > 0) {
    const candleData = formatCandleData(props.data);
    const volumeData = formatVolumeData(props.data);
    
    candleSeries.setData(candleData);
    volumeSeries.setData(volumeData);
    
    chart.timeScale().fitContent();
  }
};

// 监听数据变化，更新图表
watch(() => props.data, () => {
  if (chart) {
    updateChartData();
  }
}, { deep: true });

// 组件挂载后初始化图表
onMounted(() => {
  initChart();
});
</script>

<style scoped>
.trading-view-chart-container {
  width: 100%;
  height: 100%;
  min-height: 400px;
}

.chart-container {
  width: 100%;
  height: 100%;
}
</style> 