<template>
  <div class="app-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>主机端口与服务扫描</span>
          <el-button @click="fetchHostAssets" :icon="Refresh">刷新资产</el-button>
        </div>
      </template>

      <el-alert 
        title="端口扫描说明" 
        type="info" 
        description="此模块使用 Nmap 对目标主机的 1000 个常用端口进行扫描，并探测运行的服务版本。扫描结果将显示在“漏洞报告”页面中。" 
        show-icon 
        style="margin-bottom: 20px;"
        :closable="false"
      />

      <el-table :data="hostAssets" v-loading="loading" border style="width: 100%;">
        <el-table-column prop="id" label="资产ID" width="80" align="center" />
        <el-table-column prop="name" label="资产名称" />
        <el-table-column prop="target" label="目标 IP" />
        <el-table-column prop="created_at" label="发现时间" width="180">
          <template #default="scope">
            {{ new Date(scope.row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center">
          <template #default="scope">
            <el-button size="small" type="primary" :icon="Aim" @click="handlePortScan(scope.row)">
              扫描端口
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Aim, Refresh } from '@element-plus/icons-vue'
import request from '../utils/request'
import { useRouter } from 'vue-router'

const router = useRouter()
const hostAssets = ref([])
const loading = ref(false)

// 获取只包含 Host 类型的资产
const fetchHostAssets = async () => {
  loading.value = true
  try {
    const res = await request.get('/assets/')
    // 关键：前端只过滤出 host 类型的资产
    hostAssets.value = res.filter(item => item.asset_type === 'host')
  } catch (error) {
    console.error('获取资产失败', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchHostAssets()
})

// 提交端口扫描任务
const handlePortScan = async (row) => {
  ElMessageBox.confirm(`确定要对主机 [${row.target}] 发起端口和服务扫描吗？`, '提示', {
    confirmButtonText: '开始扫描',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    loading.value = true
    try {
      // 调用后端的 /api/assets/{id}/port_scan/ 接口
      const res = await request.post(`/assets/${row.id}/port_scan/`)
      ElMessage.success(res.message)
      // 跳转到报告页面
      router.push('/dashboard/reports')
    } catch (error) {
      console.error('发起扫描失败', error)
    } finally {
      loading.value = false
    }
  }).catch(() => {})
}
</script>

<style scoped>
.app-container {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>