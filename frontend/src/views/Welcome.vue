<template>
  <div class="welcome-container">
    <h2 style="margin-top: 0; color: #303133;">安全防护概览</h2>
    
    <el-row :gutter="20" class="stat-row">
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">管理资产总数</div>
          <div class="stat-value text-primary">
            <el-icon><Monitor /></el-icon> {{ stats.counts.assets }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">累计扫描任务</div>
          <div class="stat-value text-success">
            <el-icon><Aim /></el-icon> {{ stats.counts.tasks }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">发现漏洞总数</div>
          <div class="stat-value text-danger">
            <el-icon><Warning /></el-icon> {{ stats.counts.vulns }}
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header"><span>漏洞危险等级分布</span></div>
          </template>
          <div ref="vulnChartRef" style="height: 350px; width: 100%;"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header"><span>资产类型占比</span></div>
          </template>
          <div ref="assetChartRef" style="height: 350px; width: 100%;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { Monitor, Aim, Warning } from '@element-plus/icons-vue'
import request from '../utils/request'
import * as echarts from 'echarts' // 引入 echarts

// 响应式数据
const stats = reactive({
  counts: { assets: 0, tasks: 0, vulns: 0 },
  charts: { severity: [], asset_types: [] }
})

// 图表 DOM 的引用
const vulnChartRef = ref(null)
const assetChartRef = ref(null)

// 危险等级字典 (用于转换英文到中文及颜色)
const severityMap = {
  'critical': { name: '严重', color: '#730909' },
  'high': { name: '高危', color: '#f56c6c' },
  'medium': { name: '中危', color: '#e6a23c' },
  'low': { name: '低危', color: '#909399' },
  'info': { name: '信息', color: '#67c23a' }
}

const fetchDashboardData = async () => {
  try {
    const res = await request.get('/dashboard/stats/')
    stats.counts = res.counts
    stats.charts = res.charts
    
    // 数据获取成功后，等待 DOM 渲染完毕再初始化图表
    await nextTick()
    initVulnChart()
    initAssetChart()
  } catch (error) {
    console.error('获取首页数据失败', error)
  }
}

// 初始化漏洞等级饼图
const initVulnChart = () => {
  if (!vulnChartRef.value) return
  const chart = echarts.init(vulnChartRef.value)
  
  // 组装 ECharts 需要的格式
  const data = stats.charts.severity.map(item => ({
    name: severityMap[item.severity]?.name || item.severity,
    value: item.count,
    itemStyle: { color: severityMap[item.severity]?.color || '#ccc' }
  }))

  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [
      {
        name: '漏洞数量',
        type: 'pie',
        radius: '60%',
        data: data,
        emphasis: {
          itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' }
        }
      }
    ]
  })
}

// 初始化资产类型饼图
const initAssetChart = () => {
  if (!assetChartRef.value) return
  const chart = echarts.init(assetChartRef.value)
  
  const typeMap = { 'web': 'Web应用', 'host': '主机/服务器' }
  const data = stats.charts.asset_types.map(item => ({
    name: typeMap[item.asset_type] || item.asset_type,
    value: item.count
  }))

  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { top: 'bottom' },
    series: [
      {
        name: '资产分类',
        type: 'pie',
        radius: ['40%', '70%'], // 甜甜圈图样式
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: { show: false, position: 'center' },
        emphasis: {
          label: { show: true, fontSize: '20', fontWeight: 'bold' }
        },
        labelLine: { show: false },
        data: data
      }
    ]
  })
}

onMounted(() => {
  fetchDashboardData()
  
  // 监听窗口大小变化，自动调整图表大小以自适应屏幕
  window.addEventListener('resize', () => {
    if (vulnChartRef.value) echarts.getInstanceByDom(vulnChartRef.value)?.resize()
    if (assetChartRef.value) echarts.getInstanceByDom(assetChartRef.value)?.resize()
  })
})
</script>

<style scoped>
.welcome-container {
  padding: 20px;
}
.stat-row {
  margin-bottom: 20px;
}
.stat-card {
  text-align: center;
  padding: 10px 0;
}
.stat-title {
  color: #909399;
  font-size: 14px;
  margin-bottom: 10px;
}
.stat-value {
  font-size: 32px;
  font-weight: bold;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
}
.text-primary { color: #409EFF; }
.text-success { color: #67C23A; }
.text-danger { color: #F56C6C; }
</style>