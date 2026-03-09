<template>
  <div class="dashboard-container">
    
    <el-row :gutter="20" class="stat-row">
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card assets-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">总资产数</div>
              <div class="stat-value">
                <el-statistic :value="stats.counts.assets" />
              </div>
            </div>
            <div class="stat-icon-bg"><el-icon><Platform /></el-icon></div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card tasks-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">累计扫描任务</div>
              <div class="stat-value">
                <el-statistic :value="stats.counts.tasks" />
              </div>
            </div>
            <div class="stat-icon-bg"><el-icon><Aim /></el-icon></div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card vulns-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">发现漏洞总数 (去重后)</div>
              <div class="stat-value">
                <el-statistic :value="stats.counts.vulns" />
              </div>
            </div>
            <div class="stat-icon-bg"><el-icon><WarningFilled /></el-icon></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="header-title">漏洞风险等级分布</span>
              <el-tag type="info" effect="plain" size="small">实时去重数据</el-tag>
            </div>
          </template>
          <div ref="vulnChartRef" class="echarts-container"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="header-title">资产类型占比</span>
              <el-button type="primary" link @click="fetchStats" icon="Refresh">刷新看板</el-button>
            </div>
          </template>
          <div ref="assetChartRef" class="echarts-container"></div>
        </el-card>
      </el-col>
    </el-row>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import request from '../utils/request'
import { Platform, Aim, WarningFilled, Refresh } from '@element-plus/icons-vue'

// 存放接口返回的数据
const stats = reactive({
  counts: { assets: 0, tasks: 0, vulns: 0 },
  charts: { severity: [], asset_types: [] }
})

// 图表 DOM 引用
const vulnChartRef = ref(null)
const assetChartRef = ref(null)

// ECharts 实例
let vulnChart = null
let assetChart = null

// 危险等级的中英对照与专业配色方案 (网络安全经典警示色)
const severityConfig = {
  critical: { label: '严重', color: '#820014' }, // 深红
  high:     { label: '高危', color: '#ff4d4f' }, // 正红
  medium:   { label: '中危', color: '#fa8c16' }, // 橙色
  low:      { label: '低危', color: '#1890ff' }, // 蓝色
  info:     { label: '信息', color: '#52c41a' }, // 绿色
  unknown:  { label: '未知', color: '#8c8c8c' }  // 灰色
}

const assetTypeConfig = {
  web:  { label: 'Web 应用', color: '#722ed1' }, // 紫色
  host: { label: '主机/服务器', color: '#13c2c2' } // 青色
}

// 1. 获取后端数据
const fetchStats = async () => {
  try {
    const res = await request.get('/dashboard/stats/')
    stats.counts = res.counts
    stats.charts = res.charts
    
    // 等待 DOM 更新后渲染图表
    await nextTick()
    initVulnChart()
    initAssetChart()
  } catch (error) {
    console.error('获取首页统计数据失败', error)
  }
}

// 2. 渲染漏洞饼图 (南丁格尔玫瑰图样式)
const initVulnChart = () => {
  if (!vulnChartRef.value) return
  if (!vulnChart) vulnChart = echarts.init(vulnChartRef.value)

  // 组装 ECharts 需要的 data 数组
  const chartData = stats.charts.severity.map(item => {
    const config = severityConfig[item.severity] || severityConfig['unknown']
    return {
      value: item.count,
      name: config.label,
      itemStyle: { color: config.color }
    }
  }).sort((a, b) => a.value - b.value) // 排序让饼图更有层次

  const option = {
    tooltip: { trigger: 'item', formatter: '{a} <br/>{b} : {c} ({d}%)' },
    legend: { bottom: '0%', left: 'center' },
    series: [
      {
        name: '漏洞分布',
        type: 'pie',
        radius: ['35%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: { show: true, formatter: '{b}\n{c}个' },
        data: chartData
      }
    ]
  }
  vulnChart.setOption(option)
}

// 3. 渲染资产类型环形图
const initAssetChart = () => {
  if (!assetChartRef.value) return
  if (!assetChart) assetChart = echarts.init(assetChartRef.value)

  const chartData = stats.charts.asset_types.map(item => {
    const config = assetTypeConfig[item.asset_type] || assetTypeConfig['host']
    return {
      value: item.count,
      name: config.label,
      itemStyle: { color: config.color }
    }
  })

  const option = {
    tooltip: { trigger: 'item' },
    legend: { top: '5%', left: 'center' },
    series: [
      {
        name: '资产类型',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '60%'],
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: { show: false },
        labelLine: { show: false },
        data: chartData
      }
    ]
  }
  assetChart.setOption(option)
}

// 4. 处理浏览器窗口缩放，自适应图表大小
const handleResize = () => {
  if (vulnChart) vulnChart.resize()
  if (assetChart) assetChart.resize()
}

onMounted(() => {
  fetchStats()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (vulnChart) vulnChart.dispose()
  if (assetChart) assetChart.dispose()
})
</script>

<style scoped>
.dashboard-container {
  padding: 24px;
  background-color: #f0f2f5;
  min-height: calc(100vh - 60px);
}

/* 顶部三大统计卡片 */
.stat-row {
  margin-bottom: 24px;
}
.stat-card {
  border: none;
  border-radius: 12px;
  color: #fff;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}
.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 20px -10px rgba(0,0,0,0.15);
}

/* 渐变色主题配置 */
.assets-card { background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%); }
.tasks-card  { background: linear-gradient(135deg, #722ed1 0%, #b37feb 100%); }
.vulns-card  { background: linear-gradient(135deg, #f5222d 0%, #ff7a45 100%); }

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
}
.stat-title {
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 10px;
  font-weight: 500;
}
/* 修改 Element Plus 自带 Statistic 组件的数字颜色 */
:deep(.el-statistic__content) {
  color: #fff !important;
  font-size: 36px !important;
  font-weight: bold;
  font-family: 'Helvetica Neue', Arial, sans-serif;
}

/* 背景拟物化大图标 */
.stat-icon-bg {
  position: absolute;
  right: -20px;
  bottom: -20px;
  font-size: 120px;
  opacity: 0.15;
  transform: rotate(-15deg);
}

/* ECharts 图表卡片 */
.chart-card {
  border-radius: 12px;
  border: none;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  border-left: 4px solid #409EFF;
  padding-left: 10px;
}
.echarts-container {
  height: 350px;
  width: 100%;
}
</style>