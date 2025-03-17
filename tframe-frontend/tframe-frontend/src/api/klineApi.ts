import axios from 'axios'
import type { AxiosResponse } from 'axios'

// 定义接口返回的 K 线数据类型
// 例子
//   {
//   "date": "20250303",
//   "timestamp": "20250303 09:30:00",
//   "open": 11.52,
//   "high": 11.52,
//   "low": 11.52,
//   "close": 11.52,
//   "volume": 3726,
//   "amount": 4292352
// }
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
  from: string = '20230101', 
  to: string = '20240401', 
  interval: string = '1d'
): Promise<KlineData[]> => {
  console.log(`Fetching K-line data with params: code=${code}, from=${from}, to=${to}, interval=${interval}`);
  
  try {
    const apiUrl = 'http://tframeapi.nex.cab/api/v1/klines';
    console.log(`API URL: ${apiUrl}`);
    
    const response: AxiosResponse<KlineData[]> = await axios.get(apiUrl, {
      params: { code, from, to, interval },
      timeout: 10000 // 10秒超时
    });
    
    console.log(`API response status: ${response.status}`);
    console.log(`Received ${response.data?.length || 0} data points`);
    
    if (!response.data || response.data.length === 0) {
      console.warn('API returned empty data array');
    } else {
      // 打印第一条和最后一条数据，用于调试
      console.log('First data point:', JSON.stringify(response.data[0]));
      console.log('Last data point:', JSON.stringify(response.data[response.data.length - 1]));
      
      // 检查时间戳格式
      const firstTimestamp = response.data[0].timestamp || response.data[0].date;
      console.log('First timestamp format:', firstTimestamp);
    }
    
    return response.data || [];
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('Axios error fetching K-line data:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data
      });
    } else {
      console.error('Unknown error fetching K-line data:', error);
    }
    throw error;
  }
} 