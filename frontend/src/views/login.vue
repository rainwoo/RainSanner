<template>
  <div class="login-container">
    <div class="bg-shape shape1"></div>
    <div class="bg-shape shape2"></div>

    <div class="login-box">
      <div class="login-header">
        <h2 class="logo-title">VulnScanner</h2>
        <p class="subtitle">企业级 Web 漏洞自动化扫描平台</p>
      </div>

      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" class="login-form">
        
        <el-form-item prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="请输入账号" 
            size="large"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="请输入密码" 
            show-password
            size="large"
            :prefix-icon="Lock"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item style="margin-top: 30px;">
          <el-button 
            type="primary" 
            class="login-btn" 
            size="large" 
            :loading="loading" 
            @click="handleLogin"
          >
            立即登录
          </el-button>
        </el-form-item>

        <div class="login-footer">
          <span>还没有账号？</span>
          <el-link type="primary" :underline="false" @click="$router.push('/register')">去注册一个</el-link>
        </div>

      </el-form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '../utils/request'

const router = useRouter()
const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '账号不能为空', trigger: 'blur' }],
  password: [{ required: true, message: '密码不能为空', trigger: 'blur' }]
}

const handleLogin = () => {
  loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const res = await request.post('/login/', {
          username: loginForm.username,
          password: loginForm.password
        })
        
        // 保存 JWT Token
        localStorage.setItem('access_token', res.access)
        if (res.refresh) {
          localStorage.setItem('refresh_token', res.refresh)
        }
        
        ElMessage.success('欢迎回来，安全专家！')
        router.push('/dashboard')
      } catch (error) {
        // 请求拦截器已处理报错，此处忽略
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
/* 满屏深色渐变背景 */
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #1e222d 0%, #0e1624 100%);
  position: relative;
  overflow: hidden;
}

/* 增加科技感的发光光晕背景 */
.bg-shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  z-index: 0;
}
.shape1 {
  width: 400px;
  height: 400px;
  background: rgba(64, 158, 255, 0.15);
  top: -100px;
  left: -100px;
}
.shape2 {
  width: 300px;
  height: 300px;
  background: rgba(103, 194, 58, 0.1);
  bottom: -50px;
  right: -50px;
}

/* 核心登录卡片：白底微透光玻璃拟态 */
.login-box {
  width: 420px;
  background: rgba(255, 255, 255, 0.96);
  padding: 45px 40px;
  border-radius: 12px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  z-index: 1;
}

.login-header {
  text-align: center;
  margin-bottom: 35px;
}

.logo-title {
  margin: 0;
  font-size: 32px;
  color: #304156; /* 呼应左侧菜单的深蓝色 */
  font-weight: 800;
  letter-spacing: 1.5px;
}

.subtitle {
  margin: 10px 0 0;
  font-size: 14px;
  color: #909399;
  letter-spacing: 1px;
}

/* 按钮精美特效 */
.login-btn {
  width: 100%;
  font-size: 16px;
  font-weight: bold;
  letter-spacing: 4px;
  border-radius: 8px;
  background: linear-gradient(to right, #304156, #40536e);
  border: none;
  transition: all 0.3s ease;
}

.login-btn:hover {
  background: linear-gradient(to right, #40536e, #536987);
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(48, 65, 86, 0.3);
}

.login-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #606266;
}

/* 输入框微调，让它更圆润高级 */
:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
  padding: 4px 15px;
}
:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #304156 inset !important;
}
</style>