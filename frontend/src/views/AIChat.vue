<template>
  <div class="app-container ai-chat-container">
    <el-card class="chat-card" body-style="padding: 0; display: flex; flex-direction: column; height: calc(100vh - 140px);">
      <div class="chat-header">
        <el-icon class="header-icon"><ChatDotRound /></el-icon>
        <span>AI 安全专家助手 (SecLLM)</span>
      </div>

      <div class="chat-messages" ref="messageBox">
        <div v-for="(msg, index) in messageList" :key="index" :class="['message-wrapper', msg.role]">
          
          <el-avatar :size="40" :icon="msg.role === 'user' ? UserFilled : Service" :class="['avatar', msg.role]" />
          
          <div class="message-bubble">
            <div style="white-space: pre-wrap; line-height: 1.6;">{{ msg.content }}</div>
          </div>
        </div>
        
        <div v-if="loading" class="message-wrapper assistant">
          <el-avatar :size="40" :icon="Service" class="avatar assistant" />
          <div class="message-bubble loading-bubble">
            <el-icon class="is-loading"><Loading /></el-icon> AI 正在急速思考修复方案...
          </div>
        </div>
      </div>

      <div class="chat-input-area">
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="3"
          placeholder="把漏洞报告里的描述复制到这里，或者直接提问，例如：'如何修复 Nginx 目录遍历漏洞？给出配置代码'"
          resize="none"
          @keyup.ctrl.enter="sendMessage"
        />
        <div class="input-actions">
          <span class="hint">提示: Ctrl + Enter 快捷发送</span>
          <el-button type="primary" icon="Position" @click="sendMessage" :disabled="!inputText.trim() || loading">
            发送 (Send)
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { ChatDotRound, UserFilled, Service, Loading, Position } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '../utils/request'

const inputText = ref('')
const loading = ref(false)
const messageBox = ref(null)

// 初始打招呼消息
const messageList = ref([
  { role: 'assistant', content: '你好！我是你的专属 AI 安全专家。你可以把你扫描出来的漏洞详情发给我，我会为你提供具体的漏洞原理分析和详细的代码修复建议！' }
])

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messageBox.value) {
      messageBox.value.scrollTop = messageBox.value.scrollHeight
    }
  })
}

// 发送消息
const sendMessage = async () => {
  const text = inputText.value.trim()
  if (!text || loading.value) return

  // 1. 把用户的问题加入消息列表
  messageList.value.push({ role: 'user', content: text })
  inputText.value = ''
  scrollToBottom()

  // 2. 发送给后端 AI 接口
  loading.value = true
  try {
    const res = await request.post('/ai/ask/', { message: text })
    // 3. 将 AI 的回复加入消息列表
    messageList.value.push({ role: 'assistant', content: res.reply })
  } catch (error) {
    messageList.value.push({ role: 'assistant', content: '抱歉，服务器连接异常或 API Key 未配置，请检查后端日志。' })
    console.error('AI 接口调用失败', error)
  } finally {
    loading.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
.app-container {
  padding: 20px;
}
.chat-card {
  border-radius: 8px;
  overflow: hidden;
}
.chat-header {
  background-color: #304156;
  color: white;
  padding: 15px 20px;
  font-size: 16px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 消息滚动区 */
.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-wrapper {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  max-width: 85%;
}

/* 用户消息靠右 */
.message-wrapper.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

/* 气泡样式 */
.message-bubble {
  padding: 12px 18px;
  border-radius: 8px;
  font-size: 14px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.user .message-bubble {
  background-color: #95ec69; /* 微信绿 */
  color: #333;
  border-top-right-radius: 0;
}

.assistant .message-bubble {
  background-color: white;
  color: #333;
  border-top-left-radius: 0;
}

.loading-bubble {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
}

/* 底部输入区 */
.chat-input-area {
  padding: 15px;
  background-color: white;
  border-top: 1px solid #ebeef5;
}
.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}
.hint {
  font-size: 12px;
  color: #909399;
}
</style>