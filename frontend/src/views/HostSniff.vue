<template>
  <div class="app-container">
    <el-card class="sniff-card" style="margin-bottom: 20px;">
      <template #header>
        <div class="card-header">
          <span><el-icon><Connection /></el-icon> 内网主机自动化嗅探</span>
        </div>
      </template>

      <el-form :model="form" @submit.prevent :inline="true" class="sniff-form">
        <el-form-item label="目标网段 (CIDR)">
          <el-input v-model="form.network" placeholder="例如: 192.168.1.0/24" style="width: 250px;" clearable>
            <template #prefix><el-icon><Monitor /></el-icon></template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="warning" @click="submitSniff" :loading="loading" :icon="Location">
            开始后台嗅探
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <template #header>
        <div class="card-header" style="justify-content: space-between; width: 100%;">
          <span>嗅探任务记录</span>
          <el-button type="primary" link @click="fetchTasks" :icon="Refresh">手动刷新</el-button>
        </div>
      </template>

      <el-table :data="taskList" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="network" label="目标网段" width="160" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.status === 'pending'" type="info">等待中</el-tag>
            <el-tag v-else-if="scope.row.status === 'running'" type="primary">嗅探中</el-tag>
            <el-tag v-else-if="scope.row.status === 'completed'" type="success">已完成</el-tag>
            <el-tag v-else-if="scope.row.status === 'failed'" type="danger">失败</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="result" label="嗅探结果" />
        <el-table-column prop="created_at" label="发起时间" width="170">
          <template #default="scope">
            {{ new Date(scope.row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="finished_at" label="结束时间" width="170">
          <template #default="scope">
            {{ scope.row.finished_at ? new Date(scope.row.finished_at).toLocaleString() : '-' }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Connection, Monitor, Location, Refresh } from '@element-plus/icons-vue'
import request from '../utils/request'

const loading = ref(false)
const taskList = ref([])
let timer = null
const form = reactive({
  network: ''
})

// 获取列表数据
const fetchTasks = async () => {
  try {
    const res = await request.get('/sniff_tasks/')
    taskList.value = res
  } catch (error) {
    console.error('获取嗅探记录失败', error)
  }
}

// 提交新的嗅探任务
const submitSniff = async () => {
  if (!form.network) {
    ElMessage.warning('请输入有效的目标网段！')
    return
  }
  loading.value = true
  try {
    const res = await request.post('/assets/sniff/', { network: form.network })
    ElMessage.success(res.message)
    form.network = ''
    fetchTasks() // 立刻刷新一次列表
  } catch (error) {
    console.error('嗅探提交失败', error)
  } finally {
    loading.value = false
  }
}

// 页面加载和销毁时的轮询管理
onMounted(() => {
  fetchTasks()
  timer = setInterval(fetchTasks, 3000) // 每3秒自动刷新一次状态
})
onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.app-container {
  padding: 20px;
}
.card-header {
  font-size: 16px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
}
.sniff-form {
  display: flex;
  align-items: center;
  padding-top: 10px;
}
</style>