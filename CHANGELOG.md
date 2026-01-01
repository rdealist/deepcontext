# DeepContext 更新日志

所有项目重要的变更都会记录在此文件中。

## [1.1.0] - 2026-01-01

### 🎨 新增功能

#### 主题系统
- ✨ **完整的明暗主题系统**
  - 基于 Tailwind CSS v4 的现代化色彩系统
  - OLED 优化的深色模式（纯黑背景 #0A0A0A）
  - 系统主题自动检测 (`defaultTheme="system"`)
  - 主题状态持久化到 localStorage

- 🎨 **主题切换组件**
  - `ThemeProvider` - 主题上下文提供者
  - `ThemeToggle` - 一键切换明暗模式
  - 平滑过渡动画（200ms）
  - 避免主题切换时的闪烁 (`suppressHydrationWarning`)

#### 设计系统
- 📐 **语义化颜色令牌**
  - `--background` / `--foreground` - 页面基础色
  - `--primary` / `--primary-foreground` - 主色调（信任蓝 #2563EB）
  - `--secondary` / `--secondary-foreground` - 次要色
  - `--muted` / `--muted-foreground` - 静音状态
  - `--accent` / `--accent-foreground` - 强调色
  - `--destructive` / `--destructive-foreground` - 错误色

- 🎯 **WCAG AAA 可访问性**
  - 所有关键文字对比度 ≥ 7:1
  - 完整的键盘导航支持
  - 屏幕阅读器友好的 ARIA 标签

- ✨ **工具类扩展**
  - `.glass` - 玻璃态效果
  - `.gradient-text` - 渐变文字
  - `.scrollbar-thin` - 自定义滚动条
  - `.hover-raise` - 悬停提升效果

#### 组件更新
- 🔧 **Sidebar 组件重构**
  - 使用语义化颜色令牌
  - 添加主题切换按钮
  - Lucide 图标替代 emoji
  - 改进视觉层次和间距

- 🔧 **ChatArea 组件重构**
  - 空状态图标和提示
  - 优化的输入框样式
  - 平滑的消息滚动

- 🔧 **ChatBubble 组件重构**
  - 主题感知的气泡颜色
  - 改进的边框和阴影
  - 更好的消息区分度

### 🐛 问题修复

- 🔥 **修复 Electron 健康检查连接泄漏**
  - HTTP 请求现在正确消费响应数据
  - 防止 `CLOSE_WAIT` 连接堆积
  - 解决 Next.js 频繁被终止的问题

- 🎨 **修复 Tailwind CSS v4 兼容性**
  - 移除不兼容的 `tw-animate-css` 导入
  - 使用正确的 `@custom-variant dark` 语法
  - 确保所有主题颜色正确应用

### 📝 文档

- 📚 **新增主题设计规范** (`THEME_DESIGN.md`)
  - 完整的色彩系统说明
  - 字体和排版指南
  - 组件使用示例
  - 最佳实践和反模式
  - 可访问性要求

- 📚 **新增组件库文档** (`components/README.md`)
  - 组件开发规范
  - 样式指南
  - 响应式设计模式

### 🔄 迁移指南

#### 从旧版本升级

如果你有自定义组件，需要进行以下更新：

**旧代码:**
```tsx
<div className="bg-zinc-900 text-white">
  旧样式
</div>
```

**新代码:**
```tsx
<div className="bg-background text-foreground">
  使用主题令牌
</div>
```

#### 移除的依赖

- `tw-animate-css` - 已移除（与 Tailwind v4 不兼容）

#### 新增的依赖

- `lucide-react` - 图标库（已包含在现有依赖中）
- `class-variance-authority` - 组件变体管理（已包含）

---

## [1.0.0] - 2025-12-31

### 🎉 初始版本

- ✅ Electron + Next.js + Python FastAPI 架构
- ✅ 本地向量数据库 (LanceDB)
- ✅ Ollama 本地 LLM 集成
- ✅ Shadcn UI 组件库
- ✅ 基础的聊天界面
- ✅ 文档索引功能

---

## 📅 版本计划

### [1.2.0] - 计划中

- [ ] 深色模式下的图表优化
- [ ] 自定义主题编辑器
- [ ] 导出/导入主题配置
- [ ] 更多预设主题（蓝色、绿色、紫色）

### [1.3.0] - 计划中

- [ ] 动画主题切换效果
- [ ] 季节性主题
- [ ] 高对比度模式
- [ ] 色盲友好模式

---

## 🏷️ 版本说明

版本号遵循 [语义化版本 2.0.0](https://semver.org/lang/zh-CN/) 规范：

- **主版本号**: 不兼容的 API 变更
- **次版本号**: 向下兼容的功能新增
- **修订号**: 向下兼容的问题修复

---

**Made with ❤️ by Haru-chan (傲娇大小姐)**
