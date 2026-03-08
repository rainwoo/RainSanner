<template>
  <div class="app-container">
    <el-card class="sniff-card">
      <template #header>
        <div class="card-header">
          <span><el-icon><Radar /></el-icon> 内网主机自动化嗅探</span>
        </div>
      </template>

      <el-alert 
        title="自动化资产发现 (Ping Sweep)" 
        type="info" 
        description="请输入一个 CIDR 格式的网段（例如 192.168.1.0/24）。系统将在后台静默扫描存活主机，并将发现的 IP 自动添加到您的【资产清单】中。" 
        show-icon 
        style="margin-bottom: 30px;"
        :closable="false"
      />

      <el-form :model="form" @submit.prevent label-position="top">
        <el-form-item label="目标网段 (Target Network)">
          <el-input 
            v-model="form.network" 
            placeholder="例如: 10.0.8.0/24" 
            size="large"
            clearable
          >
            <template #prefix>
              <el-icon><Monitor /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="warning" 
            size="large" 
            @click="submitSniff" 
            :loading="loading" 
            icon="Location"
          >
            开始嗅探
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Radar, Monitor, Location } from '@element-plus/icons-vue'
import request from '../utils/request'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)
const form = reactive({
  network: ''
})

const submitSniff = async () => {
  if (!form.network) {
    ElMessage.warning('请输入有效的目标网段！')
    return
  }
  
  loading.value = true
  try {
    const res = await request.post('/assets/sniff/', {
      network: form.network
    })
    
    ElMessage.success(res.message)
    form.network = '' // 清空输入框
    
    // 提交成功后，可以引导用户去资产列表查看结果
    setTimeout(() => {
      router.push('/dashboard/assets')
    }, 2000)

  } catch (error) {
    console.error('嗅探失败', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.app-container {
  padding: 20px;
  display: flex;
  justify-content: center;
}
.sniff-card {
  width: 100%;
  max-width: 800px;
  margin-top: 20px;
}
.card-header {
  font-size: 18px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>