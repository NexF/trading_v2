import axios from 'axios'
import type { AxiosResponse } from 'axios'

// 定义接口返回的 K 线数据类型
export interface KlineData {
  date: string
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount: number
}

// K 线图表数据接口
export interface ChartData {
  time: number
  open: number
  high: number
  low: number
  close: number
}

// 成交量数据接口
export interface VolumeData {
  time: number
  value: number
  color: string
}

/**
 * 获取 K 线数据的方法
 * @param code - 股票代码
 * @param from - 开始日期
 * @param to - 结束日期
 * @param interval - 时间间隔
 * @returns Promise<KlineData[]>
 */
export const fetchKlineData = async (
  code: string = '000001.sz', 
  from: string = '20250301', 
  to: string = '20250312', 
  interval: string = '1m'
): Promise<KlineData[]> => {
  try {
    const response: AxiosResponse<KlineData[]> = await axios.get('http://tframeapi.nex.cab/api/v1/klines', {
      params: { code, from, to, interval }
    })
    return response.data
  } catch (error) {
    console.error('Failed to fetch K-line data:', error)
    throw error
  }
}

/**
 * 转换 K 线数据为图表所需格式
 * @param klineData - 原始 K 线数据
 * @returns ChartData[]
 */
export const transformKlineData = (klineData: KlineData[]): ChartData[] => {
  return klineData
    .map(item => ({
      // 将字符串时间戳转换为秒级 Unix 时间戳
      time: Math.floor(new Date(item.timestamp).getTime() / 1000),
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close
    }))
    .filter(item => !isNaN(item.time)) // 过滤掉无效时间
    .sort((a, b) => a.time - b.time)   // 确保按时间升序排序
}

/**
 * 转换成交量数据为图表所需格式
 * @param klineData - 原始 K 线数据
 * @returns VolumeData[]
 */
export const transformVolumeData = (klineData: KlineData[]): VolumeData[] => {
  return klineData.map(item => ({
    // 将字符串时间戳转换为秒级 Unix 时间戳
    time: Math.floor(new Date(item.timestamp).getTime() / 1000),
    value: item.volume,
    color: item.open <= item.close ? '#26a69a' : '#ef5350'
  })).filter(item => !isNaN(item.time)) // 过滤掉无效时间
}

/**
 * 生成演示用的K线和成交量数据
 * @returns {{klineData: Array, volumeData: Array}} 包含K线和成交量数据的对象
 */
export const generateDemoData = () => {
  const klineData = []
  const volumeData = []
  let time = new Date('2024-01-01').getTime()
  let price = 100
  
  for (let i = 0; i < 1000; i++) {
    const open = price + Math.random() * 10 - 5
    const high = open + Math.random() * 5
    const low = open - Math.random() * 5
    const close = (open + high + low) / 3
    const volume = Math.floor(Math.random() * 1000000)

    klineData.push({
      time: time / 1000,
      open,
      high: Math.max(high, open, close),
      low: Math.min(low, open, close),
      close,
    })

    volumeData.push({
      time: time / 1000,
      value: volume,
      color: close >= open ? '#26a69a' : '#ef5350',
    })

    time += 24 * 60 * 60 * 1000 // 增加一天
    price = close
  }

  return { klineData, volumeData }
}

/**
 * 计算移动平均线
 * @param data - K线数据数组
 * @param period - 移动平均期间（如MA5就是5，MA10就是10）
 * @returns 移动平均线数据数组
 */
export const calculateMA = (data: any[], period: number) => {
  const result = []
  for (let i = period - 1; i < data.length; i++) {
    let sum = 0
    for (let j = 0; j < period; j++) {
      sum += data[i - j].close
    }
    result.push({
      time: data[i].time,
      value: sum / period,
    })
  }
  return result
}

/**
 * 添加技术指标到图表
 * @param mainChart - 主图表实例
 * @param candleSeries - K线图实例
 */
export const addChartTools = (mainChart: any, candleSeries: any) => {
  if (!mainChart) return

  // 添加MA线
  const ma5Series = mainChart.addLineSeries({
    color: '#2196F3',
    lineWidth: 1,
    title: 'MA5',
  })

  const ma10Series = mainChart.addLineSeries({
    color: '#E91E63',
    lineWidth: 1,
    title: 'MA10',
  })

  // 计算并设置MA数据
  const data = candleSeries.data()
  const ma5Data = calculateMA(data, 5)
  const ma10Data = calculateMA(data, 10)

  ma5Series.setData(ma5Data)
  ma10Series.setData(ma10Data)
} 