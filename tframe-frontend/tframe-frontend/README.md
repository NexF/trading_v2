# Vue 3 + TypeScript + Vite

This template should help get you started developing with Vue 3 and TypeScript in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about the recommended Project Setup and IDE Support in the [Vue Docs TypeScript Guide](https://vuejs.org/guide/typescript/overview.html#project-setup).

# 项目结构
```
src/
├── api/          # API 请求，封装每个后端 gateway
├── assets/       # 静态资源
├── components/   # 通用组件
├── composables/  # 组合式函数
├── layouts/      # 布局组件
├── router/       # 路由配置
├── stores/       # 状态管理
├── types/        # TypeScript 类型
├── utils/        # 工具函数
└── views/        # 页面组件
```

# K线图组件使用说明

本项目包含一个基于 lightweight-charts 的 TradingViewChart 组件，用于展示股票K线图数据。

## 组件功能

TradingViewChart 组件可以：

1. 展示K线图（蜡烛图）
2. 显示交易量数据
3. 支持自定义颜色配置
4. 自动适应容器大小变化
5. 实时响应数据更新

## 使用方法

### 基本用法

```vue
<template>
  <TradingViewChart 
    :data="klineData" 
    :colors="chartColors" 
  />
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import TradingViewChart from '../components/TradingViewChart.vue';
import { fetchKlineData, type KlineData } from '../api/klineApi';

// K线数据
const klineData = ref<KlineData[]>([]);
  
// 可选：自定义颜色配置
const chartColors = reactive({
  backgroundColor: '#ffffff',
  lineColor: '#2962FF',
  textColor: '#191919',
  upColor: '#26a69a',
  downColor: '#ef5350',
  borderUpColor: '#26a69a',
  borderDownColor: '#ef5350',
  wickUpColor: '#26a69a',
  wickDownColor: '#ef5350'
});

// 获取数据
const fetchData = async () => {
  klineData.value = await fetchKlineData('000001.sz', '20230101', '20240401', '1d');
};

fetchData();
</script>
```

### 组件属性

TradingViewChart 组件接受以下属性：

- **data**: (必填) K线数据数组，类型为 `KlineData[]`
- **title**: (可选) 图表标题，默认为空
- **colors**: (可选) 自定义颜色配置对象

### 数据格式

组件接受的 K线数据格式如下：

```typescript
interface KlineData {
  date: string;       // 如 "20250303"
  timestamp: string;  // 如 "20250303 09:30:00"
  open: number;       // 开盘价
  high: number;       // 最高价
  low: number;        // 最低价
  close: number;      // 收盘价
  volume: number;     // 成交量
  amount: number;     // 成交额
}
```

## 示例页面

项目中包含一个 KlineDemo 页面，展示了如何使用该组件：

1. 通过表单控制选择股票代码、时间区间和K线类型
2. 通过 fetchKlineData API 获取数据
3. 将数据传递给 TradingViewChart 组件显示

可通过访问 `/kline-demo` 路径查看演示效果。