<template>
  <div class="kline-demo-container">
    <div class="control-panel">
      <el-form :inline="true" class="form-inline">
        <el-form-item label="股票代码">
          <el-input v-model="stockCode" placeholder="例如: 000001.sz"></el-input>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="fromDate"
            type="date"
            format="YYYYMMDD"
            value-format="YYYYMMDD"
            placeholder="选择开始日期"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="toDate"
            type="date"
            format="YYYYMMDD"
            value-format="YYYYMMDD"
            placeholder="选择结束日期"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="时间间隔">
          <el-select v-model="interval" placeholder="选择时间间隔">
            <el-option label="日K" value="1d"></el-option>
            <el-option label="周K" value="1w"></el-option>
            <el-option label="月K" value="1M"></el-option>
            <el-option label="60分钟" value="60m"></el-option>
            <el-option label="30分钟" value="30m"></el-option>
            <el-option label="15分钟" value="15m"></el-option>
            <el-option label="5分钟" value="5m"></el-option>
            <el-option label="1分钟" value="1m"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">获取数据</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="chart-container" v-loading="loading">
      <div v-if="klineData.length === 0 && !loading" class="no-data">
        请选择参数并获取数据
      </div>
      <TradingViewChart
        v-else
        :data="klineData"
        :colors="chartColors"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import TradingViewChart from '../components/TradingViewChart.vue';
import { fetchKlineData, type KlineData } from '../api/klineApi';

// 表单数据
const stockCode = ref('000001.sz');
const fromDate = ref('20230101');
const toDate = ref('20240401');
const interval = ref('1d');

// K线数据
const klineData = ref<KlineData[]>([]);
const loading = ref(false);

// 图表颜色配置
const chartColors = reactive({
  backgroundColor: '#ffffff',
  lineColor: '#2962FF',
  textColor: '#191919',
  areaTopColor: 'rgba(41, 98, 255, 0.3)',
  areaBottomColor: 'rgba(41, 98, 255, 0.0)',
  upColor: '#26a69a',
  downColor: '#ef5350',
  borderUpColor: '#26a69a',
  borderDownColor: '#ef5350',
  wickUpColor: '#26a69a',
  wickDownColor: '#ef5350'
});

// 获取K线数据
const fetchData = async () => {
  try {
    loading.value = true;
    klineData.value = await fetchKlineData(
      stockCode.value,
      fromDate.value,
      toDate.value,
      interval.value
    );
    console.log(`获取到 ${klineData.value.length} 条数据`);
  } catch (error) {
    console.error('获取K线数据失败:', error);
  } finally {
    loading.value = false;
  }
};

// 初始加载时获取数据
onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.kline-demo-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.control-panel {
  margin-bottom: 20px;
}

.chart-container {
  flex: 1;
  min-height: 500px;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  position: relative;
}

.no-data {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #999;
  font-size: 16px;
}
</style> 