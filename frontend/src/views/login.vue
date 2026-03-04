<template>
  <div class="auth-container">
    <el-card class="auth-card">
      <template #header>
        <h2 class="title">漏洞扫描平台 - 登录</h2>
      </template>
      
      <el-form :model="loginForm" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" show-password></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" class="submit-btn">登录</el-button>
        </el-form-item>
      </el-form>
      
      <div class="switch-link">
        还没有账号？ <router-link to="/register">去注册</router-link>
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

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = reactive({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
})

const handleLogin = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 2. 这里的 axios.post 改为 request.post，并且去掉前面的 http://...
        // 3. 因为响应拦截器直接返回了 response.data，所以这里可以直接拿到 data
        const data = await request.post('/login/', loginForm)
        
        // 4. 保存 Token
        localStorage.setItem('access_token', data.access)
        localStorage.setItem('refresh_token', data.refresh)
        
        ElMessage.success('登录成功！')
        router.push('/dashboard')
      } catch (error) {
        // 因为我们在拦截器里统一处理了错误提示，这里其实可以不写 ElMessage.error 了，
        // 但为了应对特定的登录失败场景，可以保留作为兜底
        console.log("登录失败", error)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
/* 样式与注册页相同 */
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