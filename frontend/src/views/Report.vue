<template>
  <div class="app-container">
    <el-card>
<template #header>
        <div class="card-header">
          <span class="title">扫描任务与报告</span>
          
          <div class="header-actions">
            <el-button type="success" plain :icon="Download" @click="exportCSV" :loading="exportLoading">
              导出 CSV
            </el-button>
            
            <el-button type="primary" plain :icon="Refresh" @click="fetchTasks">
              手动刷新
            </el-button>
          </div>
          
        </div>
      </template>

      <el-table :data="taskList" v-loading="loading" border style="width: 100%;">
        <el-table-column prop="id" label="任务ID" width="80" align="center" />
        <el-table-column prop="asset_name" label="资产名称" />
        <el-table-column prop="asset_target" label="目标地址" />
        <el-table-column prop="scan_type" label="扫描类型">
          <template #default="scope">
            {{ scope.row.scan_type === 'web_vuln' ? 'Web漏洞扫描' : '端口扫描' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.status === 'pending'" type="info">等待中</el-tag>
            <el-tag v-else-if="scope.row.status === 'running'" type="warning">扫描中</el-tag>
            <el-tag v-else-if="scope.row.status === 'completed'" type="success">已完成</el-tag>
            <el-tag v-else-if="scope.row.status === 'failed'" type="danger">失败</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ new Date(scope.row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template #default="scope">
            <el-button 
              size="small" 
              type="primary" 
              :disabled="scope.row.status !== 'completed'"
              @click="viewReport(scope.row.id)"
            >
              查看报告
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-drawer v-model="drawerVisible" title="漏洞详细报告" size="60%">
      <el-table :data="vulnList" v-loading="drawerLoading" border style="width: 100%">
<el-table-column type="expand">
          <template #default="props">
            <div class="vuln-detail-box">
              <el-descriptions :column="1" border>
                
                <el-descriptions-item label="触发位置 (URL)">
                  <el-link type="primary" :href="props.row.matched_at" target="_blank" v-if="props.row.matched_at">
                    {{ props.row.matched_at }}
                  </el-link>
                  <span v-else>暂无数据</span>
                </el-descriptions-item>

                <el-descriptions-item label="漏洞描述">
                  {{ props.row.description || '暂无详细描述' }}
                </el-descriptions-item>

                <el-descriptions-item label="提取证据 (Proof)">
                  <pre class="code-block" v-if="props.row.extracted_results">{{ props.row.extracted_results }}</pre>
                  <span v-else>暂无数据</span>
                </el-descriptions-item>

                <el-descriptions-item label="复现命令 (Curl)">
                  <pre class="code-block" v-if="props.row.curl_command">{{ props.row.curl_command }}</pre>
                  <span v-else>暂无数据</span>
                </el-descriptions-item>

                <el-descriptions-item label="修复建议">
                  {{ props.row.remediation || '暂无修复建议' }}
                </el-descriptions-item>

                <el-descriptions-item label="参考资料">
                  <pre class="code-block" v-if="props.row.references">{{ props.row.references }}</pre>
                  <span v-else>暂无数据</span>
                </el-descriptions-item>

              </el-descriptions>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="vuln_name" label="漏洞名称" />
        <el-table-column prop="severity" label="危险等级" width="120" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.severity === 'critical'" type="danger" effect="dark">严重</el-tag>
            <el-tag v-else-if="scope.row.severity === 'high'" type="danger">高危</el-tag>
            <el-tag v-else-if="scope.row.severity === 'medium'" type="warning">中危</el-tag>
            <el-tag v-else-if="scope.row.severity === 'low'" type="info">低危</el-tag>
            <el-tag v-else type="info" effect="plain">信息</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="discovered_at" label="发现时间" width="180">
          <template #default="scope">
            {{ new Date(scope.row.discovered_at).toLocaleString() }}
          </template>
        </el-table-column>
      </el-table>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Download } from '@element-plus/icons-vue'
import request from '../utils/request'

const taskList = ref([])
const loading = ref(false)

// 抽屉相关状态
const drawerVisible = ref(false)
const drawerLoading = ref(false)
const vulnList = ref([])

// 新增：导出相关的状态
const exportLoading = ref(false)

// 轮询定时器变量
let pollTimer = null

// 获取任务列表
const fetchTasks = async () => {
  try {
    const res = await request.get('/tasks/')
    taskList.value = res
  } catch (error) {
    console.error('获取任务列表失败', error)
  }
}

// 查看具体报告（漏洞列表）
const viewReport = async (taskId) => {
  drawerVisible.value = true
  drawerLoading.value = true
  try {
    // 携带 task 参数请求对应任务的漏洞
    const res = await request.get(`/vulnerabilities/?task=${taskId}`)
    vulnList.value = res
  } catch (error) {
    console.error('获取漏洞列表失败', error)
  } finally {
    drawerLoading.value = false
  }
}

// 开启轮询逻辑
const startPolling = () => {
  // 每 5000 毫秒（5秒）执行一次
  pollTimer = setInterval(async () => {
    // 检查是否还有处于 pending 或 running 状态的任务
    const hasUnfinishedTasks = taskList.value.some(
      task => task.status === 'pending' || task.status === 'running'
    )
    
    // 如果有未完成的任务，则去后端拉取最新状态
    if (hasUnfinishedTasks) {
      await fetchTasks()
    }
  }, 5000)
}

// 组件挂载时执行
onMounted(async () => {
  loading.value = true
  await fetchTasks()
  loading.value = false
  startPolling() // 获取完初始数据后，启动轮询
})

// 组件卸载时销毁定时器（非常重要！防止内存泄漏和无效请求）
onUnmounted(() => {
  if (pollTimer) {
    clearInterval(pollTimer)
  }
})

const exportCSV = async () => {
  exportLoading.value = true
  try {
    // 关键配置：responseType 必须设为 'blob'，否则 Axios 会把文件流当成乱码字符串解析
    const res = await request.get('/vulnerabilities/export/', { responseType: 'blob' })
    
    // 兼容不同的 Axios 拦截器封装方式（有的会返回 res.data，有的直接返回 res）
    const blobData = res.data || res
    
    // 构造一个 Blob 对象
    const blob = new Blob([blobData], { type: 'text/csv;charset=utf-8;' })
    
    // 利用 DOM 技巧：生成一个临时链接并模拟点击下载
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `漏洞扫描报告_${new Date().getTime()}.csv`)
    document.body.appendChild(link)
    link.click()
    
    // 清理战场
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('报告导出成功！')
  } catch (error) {
    console.error('导出失败', error)
    ElMessage.error('导出失败，请检查网络')
  } finally {
    exportLoading.value = false
  }
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
.vuln-detail {
  padding: 10px 20px;
  background-color: #f8f9fa;
  border-radius: 4px;
}
.vuln-detail-box {
  padding: 10px 25px;
  background-color: #f8f9fa;
}
/* 让提取的证据和 Curl 命令像代码块一样显示 */
.code-block {
  background-color: #2b2b2b;
  color: #a9b7c6;
  padding: 10px;
  border-radius: 4px;
  white-space: pre-wrap; /* 自动换行 */
  word-wrap: break-word;
  font-family: Consolas, Monaco, monospace;
  margin: 0;
}
.title {
  font-weight: bold;
  font-size: 16px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px; /* 增加 12px 的呼吸感间距 */
}
</style>