<template>
  <div class="login-container">
    <div class="bg-shape shape1"></div>
    <div class="bg-shape shape2"></div>

    <div class="login-box">
      <div class="login-header">
        <h2 class="logo-title">VulnScanner</h2>
        <p class="subtitle">创建您的专属安全专家账号</p>
      </div>
      
      <el-form :model="registerForm" :rules="rules" ref="formRef" class="login-form">
        
        <el-form-item prop="username">
          <el-input 
            v-model="registerForm.username" 
            placeholder="请输入用户名" 
            size="large"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item prop="email">
          <el-input 
            v-model="registerForm.email" 
            placeholder="请输入有效邮箱" 
            size="large"
            :prefix-icon="Message"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input 
            v-model="registerForm.password" 
            type="password" 
            placeholder="请输入密码" 
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        
        <el-form-item style="margin-top: 30px;">
          <el-button 
            type="primary" 
            class="login-btn" 
            size="large" 
            :loading="loading" 
            @click="handleRegister"
          >
            立即注册
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <span>已有账号？</span>
        <el-link type="primary" :underline="false" @click="$router.push('/login')">直接去登录</el-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
// 引入 Element Plus 的图标
import { User, Lock, Message } from '@element-plus/icons-vue' 
import request from '../utils/request'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

// 表单数据绑定
const registerForm = reactive({
  username: '',
  email: '',
  password: ''
})

// Element Plus 表单验证规则
const rules = reactive({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
})

// 处理注册逻辑
const handleRegister = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await request.post('/register/', registerForm)
        ElMessage.success('账号注册成功，请登录！')
        router.push('/login')
      } catch (error) {
        // 错误通常已经被拦截器拦截提示了
        console.error("注册失败", error)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
/* 满屏深色渐变背景 (复用登录页样式) */
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

/* 核心表单卡片：白底微透光玻璃拟态 */
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
  color: #304156;
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