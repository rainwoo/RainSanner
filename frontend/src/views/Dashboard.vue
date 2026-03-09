<template>
  <el-container class="layout-container">
    <el-aside width="200px" class="sidebar">
      <div class="logo-box">
        <span class="logo-text">VulnScanner</span>
      </div>
      <el-menu
        :default-active="$route.path"
        class="el-menu-vertical"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>系统首页</span>
        </el-menu-item>
        
        <el-menu-item index="/dashboard/assets">
          <el-icon><Platform /></el-icon>
          <span>资产清单</span>
        </el-menu-item>
        
        <el-menu-item index="/dashboard/sniff">
          <el-icon><Connection /></el-icon>
          <span>网络嗅探</span>
        </el-menu-item>
        
        <el-sub-menu index="scan">
          <template #title>
            <el-icon><Aim /></el-icon>
            <span>漏洞扫描</span>
          </template>
          <el-menu-item index="/dashboard/scan/web">Web 应用扫描</el-menu-item>
          <el-menu-item index="/dashboard/scan/host">主机端口扫描</el-menu-item>
        </el-sub-menu>
        
        <el-menu-item index="/dashboard/reports">
          <el-icon><Document /></el-icon>
          <span>漏洞报告</span>
        </el-menu-item>

        <el-menu-item index="/dashboard/ai">
          <el-icon><ChatDotRound /></el-icon>
          <span>AI 安全答疑</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <span>控制台</span>
        </div>
        <div class="header-right">
          <el-dropdown trigger="click">
            <span class="el-dropdown-link user-info">
              <el-avatar :size="30" :icon="UserFilled" />
              <span class="username">{{ username }}</span>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="pwdDialogVisible = true">修改密码</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view></router-view>
      </el-main>
    </el-container>

    <el-dialog title="修改密码" v-model="pwdDialogVisible" width="400px" @close="resetPwdForm">
      <el-form :model="pwdForm" :rules="pwdRules" ref="pwdFormRef" label-width="80px">
        <el-form-item label="原密码" prop="old_password">
          <el-input v-model="pwdForm.old_password" type="password" show-password placeholder="请输入当前密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="pwdForm.confirm_password" type="password" show-password placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="pwdDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitPwd" :loading="pwdLoading">确认修改</el-button>
        </span>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '../utils/request' // 引入 request
import {
  HomeFilled,
  Platform,
  Aim,
  Document,
  ChatDotRound,
  ArrowDown,
  UserFilled,
  Connection
} from '@element-plus/icons-vue'

const router = useRouter()

// ===== 用户信息逻辑 =====
const username = ref('加载中...')

const fetchUserInfo = async () => {
  try {
    const res = await request.get('/user/profile/')
    username.value = res.username
  } catch (error) {
    console.error('获取用户信息失败', error)
    username.value = '未知用户'
  }
}

onMounted(() => {
  fetchUserInfo()
})

// ===== 修改密码逻辑 =====
const pwdDialogVisible = ref(false)
const pwdLoading = ref(false)
const pwdFormRef = ref(null)

const pwdForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 自定义校验规则：确认两次密码一致
const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== pwdForm.new_password) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const pwdRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '新密码长度不能小于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' }
  ]
}

// 提交修改密码
const submitPwd = () => {
  pwdFormRef.value.validate(async (valid) => {
    if (valid) {
      pwdLoading.value = true
      try {
        const res = await request.put('/user/profile/', {
          old_password: pwdForm.old_password,
          new_password: pwdForm.new_password
        })
        ElMessage.success(res.message || '密码修改成功，请重新登录')
        pwdDialogVisible.value = false
        
        // 修改成功后强制退出重新登录
        setTimeout(() => {
          handleLogout()
        }, 1000)
      } catch (error) {
        // 错误提示通常已经在 request 拦截器里处理过了，或者后端返回 400
        console.error('修改密码失败', error)
      } finally {
        pwdLoading.value = false
      }
    }
  })
}

// 关闭弹窗时重置表单
const resetPwdForm = () => {
  if (pwdFormRef.value) {
    pwdFormRef.value.resetFields()
  }
}

// ===== 退出登录逻辑 =====
const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
/* 原有的样式完全保留 */
.layout-container {
  height: 100vh;
  width: 100%;
}
.sidebar {
  background-color: #304156;
  color: white;
  display: flex;
  flex-direction: column;
}
.logo-box {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b3649;
  color: #fff;
  font-size: 20px;
  font-weight: bold;
}
.el-menu-vertical {
  border-right: none;
  flex: 1;
}
.header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}
.header-left {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}
.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}
.username {
  margin-left: 10px;
  color: #606266;
}
.main-content {
  background-color: #f0f2f5;
  padding: 0;
}
</style>