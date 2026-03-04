<template>
  <div class="auth-container">
    <el-card class="auth-card">
      <template #header>
        <h2 class="title">漏洞扫描平台 - 注册</h2>
      </template>
      
      <el-form :model="registerForm" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" show-password></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleRegister" :loading="loading" class="submit-btn">注册</el-button>
        </el-form-item>
      </el-form>
      
      <div class="switch-link">
        已有账号？ <router-link to="/login">去登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
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
        // 2. 换成 request.post，使用相对路径
        await request.post('/register/', registerForm)
        ElMessage.success('注册成功，请登录！')
        router.push('/login')
      } catch (error) {
        // 错误通常已经被拦截器拦截提示了
        console.log("注册报错", error)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
/* 简单的居中样式 */
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}
.auth-card {
  width: 400px;
}
.title {
  text-align: center;
  margin: 0;
  color: #303133;
}
.submit-btn {
  width: 100%;
}
.switch-link {
  text-align: center;
  margin-top: 15px;
  font-size: 14px;
}
</style>