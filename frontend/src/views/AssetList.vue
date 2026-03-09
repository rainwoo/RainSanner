<template>
  <div class="app-container">
    <el-card>
      <div class="header-op">
              <el-button type="primary" @click="handleAdd" :icon="Plus">添加资产</el-button>
              <el-button @click="fetchAssets" :icon="Refresh">刷新列表</el-button>
            </div>

      <el-table :data="assetList" v-loading="loading" border style="width: 100%; margin-top: 20px;">
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="资产名称" />
        <el-table-column prop="target" label="目标地址" />
        <el-table-column prop="asset_type" label="资产类型">
          <template #default="scope">
            <el-tag :type="scope.row.asset_type === 'web' ? 'success' : 'warning'">
              {{ scope.row.asset_type === 'web' ? 'Web应用' : '主机/服务器' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="os_type" label="系统类型" align="center">
          <template #default="scope">
            <span v-if="scope.row.asset_type === 'web'">-</span>
            <el-tag v-else-if="scope.row.os_type === 'windows'" type="primary">Windows</el-tag>
            <el-tag v-else-if="scope.row.os_type === 'linux'" type="danger">Linux</el-tag>
            <el-tag v-else type="info">未知</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ new Date(scope.row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" align="center">
          <template #default="scope">
            <el-button size="small" type="success" link @click="handleScan(scope.row)">
              发起扫描
            </el-button>

            <el-button size="small" type="primary" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" link @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="资产名称" prop="name">
          <el-input v-model="form.name" placeholder="如：公司官网" />
        </el-form-item>
        <el-form-item label="目标地址" prop="target">
          <el-input v-model="form.target" placeholder="如：www.example.com 或 192.168.1.1" />
        </el-form-item>
        <el-form-item label="资产类型" prop="asset_type">
          <el-select v-model="form.asset_type" placeholder="请选择类型" style="width: 100%;">
            <el-option label="Web应用" value="web" />
            <el-option label="主机/服务器" value="host" />
          </el-select>
        </el-form-item>
        <el-form-item label="系统类型" prop="os_type" v-if="form.asset_type === 'host'">
          <el-select v-model="form.os_type" placeholder="请选择系统" style="width: 100%;">
            <el-option label="Windows" value="windows" />
            <el-option label="Linux" value="linux" />
            <el-option label="未知 (Unknown)" value="unknown" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitLoading">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../utils/request' // 引入我们封装的网络请求
import { Plus, Location, Refresh } from '@element-plus/icons-vue'

// 响应式状态变量
const assetList = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitLoading = ref(false)
const dialogTitle = ref('添加资产')
const formRef = ref(null)

// 表单数据
const form = reactive({
  id: null,
  name: '',
  target: '',
  asset_type: 'web',
  os_type: 'unknown' // 默认未知
})

// 表单校验规则
const rules = {
  name: [{ required: true, message: '请输入资产名称', trigger: 'blur' }],
  target: [{ required: true, message: '请输入目标地址', trigger: 'blur' }],
  asset_type: [{ required: true, message: '请选择资产类型', trigger: 'change' }]
}

// 获取资产列表 (Read)
const fetchAssets = async () => {
  loading.value = true
  try {
    const res = await request.get('/assets/')
    // 注意：DRF ViewSet 默认不开启分页时返回数组，开启分页时返回 { count, next, previous, results }
    // 这里假设未开启全局分页，直接赋 res
    assetList.value = res
  } catch (error) {
    console.error('获取资产列表失败', error)
  } finally {
    loading.value = false
  }
}

// 页面加载时自动获取一次数据
onMounted(() => {
  fetchAssets()
})

// 点击“添加资产”按钮
const handleAdd = () => {
  dialogTitle.value = '添加资产'
  form.id = null
  form.name = ''
  form.target = ''
  form.asset_type = 'web'
  form.os_type = 'unknown' // 重置为未知
  dialogVisible.value = true
}

// 点击“编辑”按钮
const handleEdit = (row) => {
  dialogTitle.value = '编辑资产'
  form.id = row.id
  form.name = row.name
  form.target = row.target
  form.asset_type = row.asset_type
  form.os_type = row.os_type || 'unknown' // 加载原有系统信息
  dialogVisible.value = true
}

// 提交表单 (Create & Update)
const submitForm = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (form.id) {
          // 有 id 说明是编辑 (PUT 请求)
          await request.put(`/assets/${form.id}/`, form)
          ElMessage.success('修改成功')
        } else {
          // 没有 id 说明是新增 (POST 请求)
          await request.post('/assets/', form)
          ElMessage.success('添加成功')
        }
        dialogVisible.value = false
        fetchAssets() // 重新拉取最新数据
      } catch (error) {
        console.error('保存失败', error)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// 删除资产 (Delete)
const handleDelete = (id) => {
  ElMessageBox.confirm('确定要删除该资产吗？删除后相关的扫描记录也可能丢失。', '警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await request.delete(`/assets/${id}/`)
      ElMessage.success('删除成功')
      fetchAssets()
    } catch (error) {
      console.error('删除失败', error)
    }
  }).catch(() => {
    // 用户取消操作，不做处理
  })
}

// 发起扫描逻辑 (智能分发 Web/主机 扫描)
const handleScan = async (row) => {
  // 1. 判断资产类型，决定请求接口和参数
  const isWeb = row.asset_type === 'web'
  const scanEndpoint = isWeb ? `/assets/${row.id}/scan/` : `/assets/${row.id}/port_scan/`
  // Web 资产默认带上 quick 参数，主机不需要
  const payload = isWeb ? { mode: 'quick' } : {}

  // 2. 针对不同资产类型，定制不同的提示文案
  const confirmMessage = isWeb
    ? `确定要对 Web 应用 [${row.name}] 发起扫描吗？\n\n💡 提示：此处默认为【快速扫描】模式（仅探测中高危漏洞）。\n如需执行全量深度扫描，请前往左侧菜单的“Web 扫描”页面发起。`
    : `确定要对 主机/服务器 [${row.name}] 发起【端口与服务扫描】吗？\n\n💡 提示：后台将调用 Nmap 探测其开放的端口及运行的服务版本。`

  // 3. 弹出确认框
  ElMessageBox.confirm(confirmMessage, '发起扫描', {
    confirmButtonText: '开始后台扫描',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    loading.value = true 
    try {
      // 4. 发送对应类型的扫描请求
      const res = await request.post(scanEndpoint, payload)
      ElMessage.success(res.message || '扫描任务已成功提交！')
    } catch (error) {
      console.error('扫描失败', error)
      ElMessage.error('扫描发起失败，请检查网络或后端日志')
    } finally {
      loading.value = false
    }
  }).catch(() => {
    // 用户点击取消，不做任何处理
  })
}
</script>

<style scoped>
.app-container {
  padding: 20px;
}

.header-op {
  display: flex;
  justify-content: flex-start;
  gap: 10px;
}
</style>