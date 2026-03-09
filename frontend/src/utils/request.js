// frontend/src/utils/request.js

import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router' // 引入路由用于页面跳转

// 1. 创建一个 Axios 实例
const service = axios.create({
  // 配置后端 API 的基础 URL，这样以后发请求只需写 '/login/' 即可
  baseURL: 'http://127.0.0.1:8000/api', 
  // 请求超时时间（毫秒），如果 5 秒后端还没响应，就报错
  timeout: 50000 
})

// 2. 添加【请求拦截器】
service.interceptors.request.use(
  config => {
    // 每次发送请求之前，都会执行这里的代码
    // 我们从本地存储中拿取 Token
    const token = localStorage.getItem('access_token')
    if (token) {
      // 如果有 Token，就按照 JWT 的标准格式，加到请求头里
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    // 处理请求错误
    console.error('Request Error:', error)
    return Promise.reject(error)
  }
)

// 3. 添加【响应拦截器】
service.interceptors.response.use(
  response => {
    // 2xx 范围内的状态码都会触发该函数。
    // 为了方便，我们直接返回后端返回的真实数据 (response.data)，
    // 这样在页面里用的时候就不需要再多写一层 .data 了
    return response.data
  },
  error => {
    // 超出 2xx 范围的状态码都会触发该函数。
    // 这里我们统一处理常见的 HTTP 错误状态码
    if (error.response) {
      switch (error.response.status) {
        case 400:
          ElMessage.error(error.response.data?.error || error.response.data?.detail || '请求参数错误')
          break
        case 401:
          // 401 说明没有权限或 Token 过期了
          ElMessage.warning('登录已失效，请重新登录')
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          router.push('/login') // 踢回登录页
          break
        case 403:
          ElMessage.error('没有权限执行此操作')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误，请联系管理员')
          break
        default:
          ElMessage.error(error.message || '网络请求错误')
      }
    } else {
      // 如果 error.response 不存在，可能是网络断开或后端没启动
      ElMessage.error('网络连接异常，请检查后端服务是否启动')
    }
    return Promise.reject(error)
  }
)

// 最后，将这个封装好的实例导出
export default service