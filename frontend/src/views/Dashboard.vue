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

        <el-menu-item index="/dashboard/assets">
          <el-icon><Platform /></el-icon>
          <span>资产清单</span>
        </el-menu-item>
        
        <el-menu-item index="/dashboard/sniff">
          <el-icon><Radar /></el-icon>
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
              <el-avatar :size="30" icon="UserFilled" />
              <span class="username">管理员</span>
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  HomeFilled,
  Platform,
  Aim,
  Document,
  ChatDotRound,
  ArrowDown,
  UserFilled,
  Radar  // <--- 引入这个雷达图标
} from '@element-plus/icons-vue'


const router = useRouter()

// 退出登录逻辑
const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  ElMessage.success('已安全退出')
  router.push('/login')
}
</script>

<style scoped>
/* 让整个布局撑满屏幕 */
.layout-container {
  height: 100vh;
  width: 100%;
}

/* 侧边栏样式 */
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

/* 去除菜单自带的右侧边框，使其更美观 */
.el-menu-vertical {
  border-right: none;
  flex: 1;
}

/* 顶部导航栏样式 */
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

/* 主内容区背景色稍微区别于纯白，增加层次感 */
.main-content {
  background-color: #f0f2f5;
  padding: 0; /* padding 我们放到具体的子组件里去控制 */
}
</style>