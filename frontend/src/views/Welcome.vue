<template>
  <div class="welcome-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统概览</span>
        </div>
      </template>
      <h2>欢迎使用漏洞扫描与管理平台</h2>
      <p>在这里，您可以管理您的资产、执行漏洞扫描、查看安全报告并向 AI 助手提问。</p>
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="8">
          <el-card shadow="hover" style="text-align: center;">
            <h3>资产总数</h3>
            <div style="font-size: 24px; color: #409EFF;">0</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" style="text-align: center;">
            <h3>待修复漏洞</h3>
            <div style="font-size: 24px; color: #F56C6C;">0</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" style="text-align: center;">
            <h3>扫描任务</h3>
            <div style="font-size: 24px; color: #67C23A;">0</div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<style scoped>
.welcome-container {
  padding: 20px;
}
</style>