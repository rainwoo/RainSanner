<template>
  <div class="app-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Web 应用漏洞扫描</span>
          <el-button @click="fetchWebAssets" :icon="Refresh">刷新资产</el-button>
        </div>
      </template>
      <el-alert 
        title="Web 漏洞扫描说明" 
        type="info" 
        description="此模块基于 Nuclei 引擎对 Web 应用进行指纹识别与漏洞探测。支持【快速扫描】（仅探测中高危）和【深度扫描】（全量指纹与低危探测）。扫描结果将自动汇总在“漏洞报告”页面中，并支持 AI 智能修复答疑。" 
        show-icon 
        style="margin-bottom: 20px;"
        :closable="false"
      />

      <el-table :data="webAssets" v-loading="loading" border style="width: 100%;">
        <el-table-column prop="id" label="资产ID" width="80" align="center" />
        <el-table-column prop="name" label="资产名称" />
        <el-table-column prop="target" label="目标 URL" />
        <el-table-column label="操作" width="150" align="center">
          <template #default="scope">
            <el-button class="Scanbtn" size="small" type="success" icon="Aim" @click="openScanDialog(scope.row)">
            发起扫描
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="配置扫描任务" width="400px">
      <div v-if="selectedAsset" style="margin-bottom: 20px;">
        <strong>目标：</strong> {{ selectedAsset.name }} ({{ selectedAsset.target }})
      </div>
      
      <el-form label-position="top">
        <el-form-item label="选择扫描模式：">
          <el-radio-group v-model="scanMode" class="mode-selector">
            <el-radio-button label="quick" value="quick">
              <el-icon><Lightning /></el-icon> 快速扫描
            </el-radio-button>
            <el-radio-button label="deep" value="deep">
              <el-icon><Search /></el-icon> 深度扫描
            </el-radio-button>
          </el-radio-group>
        </el-form-item>
        
        <el-alert v-if="scanMode === 'quick'" title="快速扫描说明" type="success" :closable="false"
          description="仅探测严重(Critical)与高危(High)漏洞。扫描速度快，耗时极短，适用于日常快速巡检。" />
        <el-alert v-if="scanMode === 'deep'" title="深度扫描说明" type="warning" :closable="false"
          description="探测全部中高低危漏洞。扫描耗时较长（可能数十分钟），会对目标产生较多请求，适用于全面安全体检。" />
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitScan" :loading="submitLoading">开始执行</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Lightning, Search, Aim } from '@element-plus/icons-vue'
import request from '../utils/request'
import { useRouter } from 'vue-router'

const router = useRouter()
const webAssets = ref([])
const loading = ref(false)

// 弹窗相关状态
const dialogVisible = ref(false)
const submitLoading = ref(false)
const selectedAsset = ref(null)
const scanMode = ref('quick') // 默认选择快速扫描

// 获取只包含 Web 类型的资产
const fetchWebAssets = async () => {
  loading.value = true
  try {
    const res = await request.get('/assets/')
    // 前端过滤出 web 类型的资产
    webAssets.value = res.filter(item => item.asset_type === 'web')
  } catch (error) {
    console.error('获取资产失败', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchWebAssets()
})

// 打开配置弹窗
const openScanDialog = (row) => {
  selectedAsset.value = row
  scanMode.value = 'quick' // 每次打开重置为快速模式
  dialogVisible.value = true
}

// 提交扫描任务
const submitScan = async () => {
  submitLoading.value = true
  try {
    // 将用户选择的模式作为参数 POST 给后端
    const res = await request.post(`/assets/${selectedAsset.value.id}/scan/`, {
      mode: scanMode.value
    })
    ElMessage.success(res.message)
    dialogVisible.value = false
    
    // 提交成功后，直接跳转到报告页面去查看进度
    router.push('/dashboard/reports')
  } catch (error) {
    console.error('发起扫描失败', error)
  } finally {
    submitLoading.value = false
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
.mode-selector {
  display: flex;
  width: 100%;
}
.mode-selector :deep(.el-radio-button) {
  flex: 1;
}
.mode-selector :deep(.el-radio-button__inner) {
  width: 100%;
}
.Scanbtn {
  width: 50%;
  text-align: center;
}
</style>