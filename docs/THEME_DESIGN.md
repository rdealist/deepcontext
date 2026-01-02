# DeepContext 主题设计规范

> 📅 创建日期: 2026-01-01
> 🎨 设计系统: Minimalism + Dark Mode (OLED)
> 📦 版本: 1.0.0

---

## 📋 目录

1. [设计原则](#设计原则)
2. [色彩系统](#色彩系统)
3. [字体系统](#字体系统)
4. [组件规范](#组件规范)
5. [间距与布局](#间距与布局)
6. [动画与交互](#动画与交互)
7. [可访问性](#可访问性)
8. [代码示例](#代码示例)

---

## 🎯 设计原则

### 核心理念

- **极简主义 (Minimalism)**: 去除不必要的视觉元素，专注内容本身
- **专业感 (Professional)**: 使用标准 SaaS 色板，传递信任感
- **可读性优先 (Readability First)**: 确保在所有环境下文字都清晰可读
- **OLED 优化 (OLED Optimized)**: 深色模式使用纯黑背景，节省电量并提升对比度

### 设计语言

```
专业 + 现代 + 高效 = DeepContext
```

---

## 🎨 色彩系统

### 色彩架构

采用语义化色彩令牌 (Semantic Color Tokens)，所有颜色通过 CSS 变量管理，支持明暗主题无缝切换。

### Light Mode (浅色模式)

#### 基础色板

| 令牌名称 | HSL 值 | 十六进制 | 用途 | 对比度 |
|---------|--------|---------|------|--------|
| `--background` | `0 0% 100%` | `#FFFFFF` | 页面背景 | - |
| `--foreground` | `240 10% 3.9%` | `#0A0A0A` | 主要文字 | 21:1 ✅ |
| `--card` | `0 0% 100%` | `#FFFFFF` | 卡片背景 | - |
| `--border` | `240 5.9% 90%` | `#E5E7EB` | 边框线条 | - |

#### 语义色

| 令牌名称 | HSL 值 | 十六进制 | 用途 |
|---------|--------|---------|------|
| `--primary` | `221 83% 53%` | `#2563EB` | 主色调、CTA 按钮 |
| `--primary-foreground` | `0 0% 98%` | `#FAFAFA` | 主色上的文字 |
| `--secondary` | `240 4.8% 95.9%` | `#F3F4F6` | 次要背景 |
| `--secondary-foreground` | `240 5.9% 10%` | `#1A1A1A` | 次要背景上的文字 |
| `--muted` | `240 4.8% 95.9%` | `#F3F4F6` | 静音状态背景 |
| `--muted-foreground` | `240 3.8% 46.1%` | `#6B7280` | 静音文字、占位符 |
| `--accent` | `240 4.8% 95.9%` | `#F3F4F6` | 强调背景 |
| `--accent-foreground` | `240 5.9% 10%` | `#1A1A1A` | 强调背景上的文字 |
| `--destructive` | `0 84.2% 60.2%` | `#EF4444` | 错误、危险操作 |
| `--destructive-foreground` | `0 0% 98%` | `#FAFAFA` | 危险色上的文字 |

### Dark Mode (深色模式)

#### 基础色板 (OLED 优化)

| 令牌名称 | HSL 值 | 十六进制 | 用途 | 对比度 |
|---------|--------|---------|------|--------|
| `--background` | `0 0% 3.9%` | `#0A0A0A` | 页面背景 (纯黑) | - |
| `--foreground` | `0 0% 98%` | `#FAFAFA` | 主要文字 | 20:1 ✅ |
| `--card` | `0 0% 3.9%` | `#0A0A0A` | 卡片背景 | - |
| `--border` | `240 3.7% 15.9%` | `#292929` | 边框线条 | - |

#### 语义色

| 令牌名称 | HSL 值 | 十六进制 | 用途 |
|---------|--------|---------|------|
| `--primary` | `217 91% 60%` | `#3B82F6` | 主色调 (增强亮度) |
| `--primary-foreground` | `0 0% 98%` | `#FAFAFA` | 主色上的文字 |
| `--secondary` | `240 3.7% 15.9%` | `#292929` | 次要背景 |
| `--secondary-foreground` | `0 0% 98%` | `#FAFAFA` | 次要背景上的文字 |
| `--muted` | `240 3.7% 15.9%` | `#292929` | 静音状态背景 |
| `--muted-foreground` | `240 5% 64.9%` | `#A1A1AA` | 静音文字 |
| `--accent` | `240 3.7% 15.9%` | `#292929` | 强调背景 |
| `--accent-foreground` | `0 0% 98%` | `#FAFAFA` | 强调背景上的文字 |
| `--destructive` | `0 72% 51%` | `#E11D48` | 错误 (增强红色) |
| `--destructive-foreground` | `0 0% 98%` | `#FAFAFA` | 危险色上的文字 |

### 色彩使用指南

#### ✅ 正确使用

```tsx
{/* 使用语义化颜色令牌 */}
<Button className="bg-primary text-primary-foreground">
  主要操作
</Button>

<div className="bg-muted text-muted-foreground">
  辅助信息
</div>

<p className="text-destructive">
  错误提示
</p>
```

#### ❌ 错误使用

```tsx
{/* 不要硬编码颜色 */}
<Button className="bg-[#2563EB] text-white">
  错误示例
</Button>

{/* 不要在深色模式使用低对比度颜色 */}
<div className="dark:bg-white/10 dark:text-gray-400">
  对比度不足
</div>
```

---

## 🔤 字体系统

### 字体家族

#### Geist Sans (正文)

```css
font-family: var(--font-geist-sans), sans-serif;
```

- **用途**: 所有正文、标题、UI 文本
- **风格**: 现代、简洁、高可读性
- **字重**: 400 (Regular), 500 (Medium), 600 (SemiBold), 700 (Bold)

#### Geist Mono (代码)

```css
font-family: var(--font-geist-mono), monospace;
```

- **用途**: 代码片段、文件路径、技术内容
- **风格**: 等宽、专业
- **字重**: 400 (Regular), 500 (Medium)

### 字体大小

| Tailwind 类 | 大小 | 用途 |
|------------|------|------|
| `text-xs` | 12px | 标签、辅助信息 |
| `text-sm` | 14px | 正文、描述 |
| `text-base` | 16px | 默认正文 |
| `text-lg` | 18px | 小标题 |
| `text-xl` | 20px | 页面标题 |
| `text-2xl` | 24px | 区域标题 |

### 字重

| Tailwind 类 | 字重 | 用途 |
|------------|------|------|
| `font-normal` | 400 | 正文 |
| `font-medium` | 500 | 强调文字 |
| `font-semibold` | 600 | 小标题 |
| `font-bold` | 700 | 主标题 |

---

## 🧩 组件规范

### Button (按钮)

#### 变体

```tsx
// Default - 主要操作
<Button className="bg-primary text-primary-foreground hover:bg-primary/90">
  保存
</Button>

// Outline - 次要操作
<Button variant="outline" className="hover:bg-accent hover:text-accent-foreground">
  取消
</Button>

// Ghost - 低优先级操作
<Button variant="ghost" className="text-muted-foreground hover:bg-accent hover:text-accent-foreground">
  清除
</Button>

// Destructive - 危险操作
<Button variant="destructive" className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
  删除
</Button>
```

#### 状态

```tsx
// 禁用状态
<Button disabled>
  禁用按钮
</Button>

// 加载状态
<Button disabled>
  <Loader className="mr-2 h-4 w-4 animate-spin" />
  处理中...
</Button>
```

### Card (卡片)

```tsx
<Card className="border-border bg-card/50 backdrop-blur-sm">
  <CardHeader>
    <CardTitle className="text-foreground">卡片标题</CardTitle>
  </CardHeader>
  <CardContent>
    <p className="text-muted-foreground">卡片内容</p>
  </CardContent>
</Card>
```

### Input (输入框)

```tsx
<Input
  placeholder="请输入内容..."
  className="bg-background border-border focus-visible:ring-primary"
/>
```

---

## 📐 间距与布局

### 间距系统

基于 Tailwind 默认间距系统:

| 类 | 大小 | 用途 |
|---|------|------|
| `p-4` | 16px | 标准内边距 |
| `p-6` | 24px | 大区域内边距 |
| `gap-2` | 8px | 紧密间距 |
| `gap-4` | 16px | 标准间距 |
| `gap-6` | 24px | 宽松间距 |

### 布局原则

1. **容器宽度**: 使用 `max-w-*` 限制内容宽度
2. **响应式**: `px-4 md:px-6 lg:px-8` 渐进式内边距
3. **Grid 系统**: 12 列网格用于复杂布局

---

## ✨ 动画与交互

### 过渡时长

| 状态 | 时长 | 用途 |
|-----|------|------|
| 快速 | 150ms | 悬停效果 |
| 标准 | 200ms | 颜色变化 |
| 慢速 | 300ms | 布局变化 |

### 主题切换动画

```css
/* 全局过渡 */
*,
*::before,
*::after {
  transition-property: color, background-color, border-color;
  transition-duration: 200ms;
}
```

### 悬停效果

```tsx
// 颜色变化 (推荐)
<div className="hover:bg-accent transition-colors duration-200">
  悬停我
</div>

// 轻微位移 (谨慎使用)
<div className="hover:-translate-y-0.5 transition-transform duration-200">
  卡片效果
</div>
```

---

## ♿ 可访问性

### 对比度要求

- **WCAG AA**: 最小 4.5:1 (普通文字), 3:1 (大文字)
- **WCAG AAA**: 最小 7:1 (普通文字), 4.5:1 (大文字)
- **本系统**: 所有关键文字均达到 AAA 标准

### 焦点状态

```css
:focus-visible {
  outline: 2px solid hsl(var(--ring));
  outline-offset: 2px;
}
```

### 屏幕阅读器

```tsx
// 图标按钮需要文字说明
<button aria-label="切换主题">
  <ThemeIcon />
</button>

// 错误消息需要 role="alert"
<div role="alert" aria-live="polite">
  {errorMessage}
</div>
```

### 键盘导航

- 所有交互元素支持键盘访问
- Tab 顺序符合视觉流
- Enter/Space 激活按钮

---

## 💻 代码示例

### 使用主题提供者

```tsx
import { ThemeProvider } from "@/components/theme-provider";

export default function RootLayout({ children }) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body>
        <ThemeProvider defaultTheme="system" storageKey="deepcontext-theme">
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
```

### 主题切换器

```tsx
import { ThemeToggle } from "@/components/theme-toggle";

export function Navbar() {
  return (
    <nav className="flex items-center justify-between border-b border-border bg-card p-4">
      <h1 className="text-xl font-bold text-foreground">Logo</h1>
      <ThemeToggle />
    </nav>
  );
}
```

### 主题感知组件

```tsx
import { useTheme } from "@/components/theme-provider";

export function ThemedComponent() {
  const { theme } = useTheme();
  
  return (
    <div className="bg-background text-foreground border border-border rounded-lg p-4">
      <p>当前主题: {theme}</p>
      <p className="text-muted-foreground">这段文字会自动适配明暗模式</p>
    </div>
  );
}
```

### 自定义颜色工具类

```tsx
// 使用 HSL 值直接创建变体
<div className="bg-primary/10 text-primary">
  主色调的 10% 透明度背景
</div>

<div className="bg-muted-foreground/20">
  静音前景色的 20% 透明度
</div>
```

---

## 📦 工具类

### 玻璃态效果

```tsx
<div className="glass">
  默认玻璃态 (bg-background/80)
</div>

<div className="glass-light">
  浅色玻璃态 (bg-white/80)
</div>

<div className="glass-dark">
  深色玻璃态 (bg-black/80)
</div>
```

### 渐变文字

```tsx
<h1 className="gradient-text">
  渐变标题文字
</h1>
```

### 自定义滚动条

```tsx
<div className="scrollbar-thin">
  内容区域
</div>
```

---

## 🚀 最佳实践

### ✅ DO (推荐做法)

1. **始终使用语义化颜色令牌**
   ```tsx
   <div className="bg-card text-card-foreground">✅</div>
   ```

2. **为交互元素添加 cursor-pointer**
   ```tsx
   <div className="cursor-pointer hover:bg-accent">✅</div>
   ```

3. **提供明确的悬停反馈**
   ```tsx
   <Button className="hover:bg-primary/90 transition-colors duration-200">
     ✅
   </Button>
   ```

4. **使用一致的圆角**
   ```tsx
   <div className="rounded-lg">✅ 统一使用 rounded-lg/md</div>
   ```

### ❌ DON'T (避免做法)

1. **不要硬编码颜色**
   ```tsx
   <div className="bg-[#2563EB]">❌</div>
   ```

2. **不要使用 emoji 作为图标**
   ```tsx
   <span>📁 文件夹</span> ❌
   <Folder className="h-4 w-4" /> ✅
   ```

3. **不要在浅色模式使用过度透明**
   ```tsx
   <div className="bg-white/10">❌ 看不见</div>
   <div className="bg-white/80">✅ 正确</div>
   ```

4. **不要使用 scale 做悬停效果**
   ```tsx
   <div className="hover:scale-105">❌ 会导致布局偏移</div>
   ```

---

## 📝 更新日志

### v1.0.0 (2026-01-01)

- ✨ 初始主题系统
- 🎨 完整的明暗主题支持
- ♿ WCAG AAA 可访问性标准
- 📱 响应式设计支持
- 🚀 OLED 优化的深色模式

---

## 🔗 相关资源

- [Tailwind CSS 文档](https://tailwindcss.com/docs)
- [Radix UI Primitives](https://www.radix-ui.com/primitives)
- [shadcn/ui 组件](https://ui.shadcn.com)
- [WCAG 2.1 标准](https://www.w3.org/WAI/WCAG21/quickref/)

---

**Made with ❤️ by Haru-chan (傲娇大小姐)**
