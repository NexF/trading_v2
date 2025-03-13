import { fetchKlineData } from '../api/klineApi'
import type { KlineData } from '../api/klineApi'

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
 * 解析时间戳字符串为Unix时间戳（秒）
 * @param timestampStr - 时间戳字符串，支持多种格式
 * @returns number - Unix时间戳（秒）
 */
export const parseTimestamp = (timestampStr: string): number => {
  
  // 如果输入为空，返回当前时间
  if (!timestampStr) {
    console.warn('Empty timestamp string received, using current time');
    return Math.floor(Date.now() / 1000);
  }
  
  // 处理格式为 "20250303 09:30:00" 的时间戳
  const dateMatch = /^(\d{4})(\d{2})(\d{2})\s+(\d{2}):(\d{2}):(\d{2})$/.exec(timestampStr);
  
  if (dateMatch) {
    const [_, year, month, day, hour, minute, second] = dateMatch;
    // 注意：JavaScript中月份是从0开始的，所以需要减1
    const date = new Date(
      parseInt(year),
      parseInt(month) - 1,
      parseInt(day),
      parseInt(hour),
      parseInt(minute),
      parseInt(second)
    );
    const timestamp = Math.floor(date.getTime() / 1000);
    return timestamp;
  }
  
  // 处理格式为 "20250303" 的日期
  const dateOnlyMatch = /^(\d{4})(\d{2})(\d{2})$/.exec(timestampStr);
  if (dateOnlyMatch) {
    const [_, year, month, day] = dateOnlyMatch;
    const date = new Date(
      parseInt(year),
      parseInt(month) - 1,
      parseInt(day),
      0, 0, 0
    );
    const timestamp = Math.floor(date.getTime() / 1000);
    return timestamp;
  }
  
  // 尝试处理ISO格式的时间戳 (如 "2025-03-03T09:30:00")
  if (timestampStr.includes('T') || timestampStr.includes('-')) {
    const timestamp = Math.floor(new Date(timestampStr).getTime() / 1000);
    return timestamp;
  }
  
  // 尝试处理纯数字的时间戳
  if (/^\d+$/.test(timestampStr)) {
    const numValue = parseInt(timestampStr);
    
    // 如果是13位（毫秒级时间戳），转换为秒级
    if (timestampStr.length === 13) {
      const timestamp = Math.floor(numValue / 1000);
      console.log(`Parsed millisecond timestamp ${timestampStr} to ${timestamp}`);
      return timestamp;
    }
    // 如果是10位（秒级时间戳），直接返回
    if (timestampStr.length === 10) {
      console.log(`Parsed second timestamp ${timestampStr} to ${numValue}`);
      return numValue;
    }
    
    // 其他长度的数字，尝试判断是否是合理的时间戳
    const year2000 = 946684800; // 2000-01-01 的Unix时间戳
    const year2050 = 2524608000; // 2050-01-01 的Unix时间戳
    
    if (numValue >= year2000 && numValue <= year2050) {
      console.log(`Parsed numeric timestamp ${timestampStr} to ${numValue}`);
      return numValue;
    } else if (numValue >= year2000 * 1000 && numValue <= year2050 * 1000) {
      // 可能是毫秒级时间戳
      const timestamp = Math.floor(numValue / 1000);
      console.log(`Converted millisecond timestamp ${timestampStr} to ${timestamp}`);
      return timestamp;
    }
  }
  
  // 如果不匹配预期格式，尝试标准Date解析（兼容旧格式）
  try {
    const timestamp = Math.floor(new Date(timestampStr).getTime() / 1000);
    
    // 检查解析结果是否合理
    if (isNaN(timestamp)) {
      console.warn(`Failed to parse timestamp: ${timestampStr}, using current time`);
      return Math.floor(Date.now() / 1000);
    }
    
    console.log(`Fallback parsing of ${timestampStr} to ${timestamp}`);
    return timestamp;
  } catch (error) {
    console.error(`Error parsing timestamp: ${timestampStr}`, error);
    return Math.floor(Date.now() / 1000);
  }
}

/**
 * 转换 K 线数据为图表所需格式
 * @param klineData - 原始 K 线数据
 * @returns ChartData[]
 */
export const transformKlineData = (klineData: KlineData[]): ChartData[] => {
  if (klineData.length <= 0) {
    console.warn('Empty klineData array received!');
    return [];
  }
  
  const transformed: ChartData[] = klineData
    .map(item => {
      try {
        // 优先使用timestamp字段，如果不存在则使用date字段
        const timestampStr = item.timestamp || item.date;
        
        if (!timestampStr) {
          console.warn('Missing timestamp and date in data point:', item);
          return null;
        }
        
        // 确保时间戳是整数
        let timeValue = Math.floor(parseTimestamp(timestampStr));
        
        // 检查时间戳是否合理（2000年到2050年之间）
        const year2000 = 946684800; // 2000-01-01 的Unix时间戳
        const year2050 = 2524608000; // 2050-01-01 的Unix时间戳
        
        if (timeValue < year2000 || timeValue > year2050) {
          console.warn(`Suspicious timestamp value: ${timeValue}, original: ${timestampStr}`);
          // 如果时间戳不合理，尝试修复（可能是毫秒级时间戳）
          if (timeValue > year2050 * 1000) {
            timeValue = Math.floor(timeValue / 1000);
            console.log(`Converted to seconds: ${timeValue}`);
          }
        }
        
        // 确保所有数值都是数字类型
        const open = typeof item.open === 'string' ? parseFloat(item.open) : Number(item.open);
        const high = typeof item.high === 'string' ? parseFloat(item.high) : Number(item.high);
        const low = typeof item.low === 'string' ? parseFloat(item.low) : Number(item.low);
        const close = typeof item.close === 'string' ? parseFloat(item.close) : Number(item.close);
        
        // 检查数据是否有效
        if (isNaN(open) || isNaN(high) || isNaN(low) || isNaN(close) || isNaN(timeValue)) {
          console.warn('Invalid data point:', {
            original: item,
            parsed: { time: timeValue, open, high, low, close }
          });
          return null;
        }
        
        return {
          time: timeValue,
          open,
          high,
          low,
          close
        };
      } catch (error) {
        console.error('Error processing data point:', item, error);
        return null;
      }
    })
    .filter((item): item is ChartData => item !== null && 
                   !isNaN(item.time) && 
                   item.open !== undefined && 
                   item.high !== undefined && 
                   item.low !== undefined && 
                   item.close !== undefined &&
                   !isNaN(item.open) &&
                   !isNaN(item.high) &&
                   !isNaN(item.low) &&
                   !isNaN(item.close) &&
                   // 确保价格数据合理
                   item.high >= item.low &&
                   item.high >= 0 &&
                   item.low >= 0
    ) // 过滤掉无效时间和数据
    .sort((a, b) => a.time - b.time);   // 确保按时间升序排序
  
  // 如果转换后的数据为空，记录警告
  if (transformed.length === 0) {
    console.error('No valid data after transformation! All data was filtered out.');
  }
  
  return transformed;
}

/**
 * 转换成交量数据为图表所需格式
 * @param klineData - 原始 K 线数据
 * @returns VolumeData[]
 */
export const transformVolumeData = (klineData: KlineData[]): VolumeData[] => {  
  if (klineData.length === 0) {
    console.warn('Empty klineData array received for volume data!');
    return [];
  }
  
  const transformed: VolumeData[] = klineData
    .map(item => {
      try {
        // 优先使用timestamp字段，如果不存在则使用date字段
        const timestampStr = item.timestamp || item.date;
        
        if (!timestampStr) {
          console.warn('Missing timestamp and date in volume data point:', item);
          return null;
        }
        
        // 确保时间戳是整数
        let timeValue = Math.floor(parseTimestamp(timestampStr));
        
        // 检查时间戳是否合理（2000年到2050年之间）
        const year2000 = 946684800; // 2000-01-01 的Unix时间戳
        const year2050 = 2524608000; // 2050-01-01 的Unix时间戳
        
        if (timeValue < year2000 || timeValue > year2050) {
          console.warn(`Suspicious timestamp value for volume: ${timeValue}, original: ${timestampStr}`);
          // 如果时间戳不合理，尝试修复（可能是毫秒级时间戳）
          if (timeValue > year2050 * 1000) {
            timeValue = Math.floor(timeValue / 1000);
          }
        }
        
        // 确保成交量是数字类型
        const volume = typeof item.volume === 'string' ? parseFloat(item.volume) : Number(item.volume);
        
        // 确保开盘价和收盘价是数字类型
        const open = typeof item.open === 'string' ? parseFloat(item.open) : Number(item.open);
        const close = typeof item.close === 'string' ? parseFloat(item.close) : Number(item.close);
        
        // 检查数据是否有效
        if (isNaN(volume) || isNaN(timeValue) || isNaN(open) || isNaN(close)) {
          console.warn('Invalid volume data point:', {
            original: item,
            parsed: { time: timeValue, value: volume, open, close }
          });
          return null;
        }
        
        return {
          time: timeValue,
          value: volume,
          color: open <= close ? '#26a69a' : '#ef5350'
        };
      } catch (error) {
        console.error('Error processing volume data point:', item, error);
        return null;
      }
    })
    .filter((item): item is VolumeData => 
      item !== null && 
      !isNaN(item.time) && 
      !isNaN(item.value) && 
      item.value >= 0
    ) // 过滤掉无效时间和数据
    .sort((a, b) => a.time - b.time); // 确保按时间升序排序
  
  
  if (transformed.length === 0) {
    console.error('No valid volume data after transformation! All data was filtered out.');
  } else {
    console.log('Volume data sample (first item):', JSON.stringify(transformed[0]));
  }
  
  return transformed;
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

  // 获取K线数据
  const data = candleSeries.data()
  
  // 如果数据为空或长度不足，不添加MA线
  if (!data || data.length < 10) {
    console.warn('Not enough data for MA calculation, skipping MA lines')
    return
  }

  try {
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
    const ma5Data = calculateMA(data, 5)
    const ma10Data = calculateMA(data, 10)

    ma5Series.setData(ma5Data)
    ma10Series.setData(ma10Data)
  } catch (error) {
    console.error('Error adding chart tools:', error)
  }
} 