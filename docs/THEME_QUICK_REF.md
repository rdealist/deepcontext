# DeepContext 主题快速参考

> 快速查找常用的主题类名和代码片段

## 🎨 常用颜色类

### 基础色

```tsx
// 页面背景和文字
<div className="bg-background text-foreground">

// 卡片
<div className="bg-card text-card-foreground border-border">

// 次要背景
<div className="bg-muted text-muted-foreground">
```

### 语义色

```tsx
// 主色调（蓝色）
<div className="bg-primary text-primary-foreground">
<div className="text-primary">文字色</div>
<div className="border-primary">边框</div>
<div className="bg-primary/10">淡化背景</div>

// 强调色
<div className="bg-accent text-accent-foreground hover:bg-accent/80">

// 错误/危险
<div className="bg-destructive text-destructive-foreground">
<div className="text-destructive">错误文字</div>
```

## 🧩 组件类

### 按钮

```tsx
// 主要按钮
<Button className="bg-primary text-primary-foreground hover:bg-primary/90">

// 次要按钮
<Button variant="outline" className="hover:bg-accent">

// 幽灵按钮
<Button variant="ghost" className="text-muted-foreground hover:text-accent-foreground">

// 危险按钮
<Button variant="destructive" className="bg-destructive hover:bg-destructive/90">
```

### 输入框

```tsx
<Input className="bg-background border-border focus-visible:ring-primary" />
```

### 卡片

```tsx
<Card className="border-border bg-card/50 backdrop-blur-sm">
  <CardHeader>
    <CardTitle className="text-foreground">标题</CardTitle>
  </CardHeader>
  <CardContent>
    <p className="text-muted-foreground">内容</p>
  </CardContent>
</Card>
```

## 📐 间距类

```tsx
// 内边距
<div className="p-4">  // 16px 标准
<div className="p-6">  // 24px 大

// 外边距
<div className="m-4">
<div className="mx-auto">  // 水平居中

// 间隙
<div className="gap-2">  // 8px 紧密
<div className="gap-4">  // 16px 标准
```

## ✨ 效果类

```tsx
// 圆角
<div className="rounded-md">  // 中等
<div className="rounded-lg">  // 大
<div className="rounded-xl">  // 超大
<div className="rounded-full">  // 完全圆形

// 阴影
<div className="shadow-sm">  // 小阴影
<div className="shadow">  // 默认
<div className="shadow-lg">  // 大阴影

// 玻璃态
<div className="glass">  // 默认玻璃态
<div className="backdrop-blur-xl bg-background/80">  // 自定义

// 渐变文字
<h1 className="gradient-text">  // 主色调渐变
```

## 🎭 文字类

```tsx
// 大小
<p className="text-xs">  // 12px
<p className="text-sm">  // 14px
<p className="text-base">  // 16px
<p className="text-lg">  // 18px
<p className="text-xl">  // 20px

// 字重
<p className="font-normal">  // 400
<p className="font-medium">  // 500
<p className="font-semibold">  // 600
<p className="font-bold">  // 700

// 颜色
<p className="text-foreground">  // 主要文字
<p className="text-muted-foreground">  // 次要文字
<p className="text-primary">  // 主色调文字
<p className="text-destructive">  // 错误文字
```

## 🎯 状态类

```tsx
// 悬停
<div className="hover:bg-accent cursor-pointer transition-colors duration-200">

// 禁用
<Button disabled className="opacity-50 cursor-not-allowed">

// 加载
<div className="animate-pulse">  // 脉冲动画
<div className="animate-spin">  // 旋转动画

// 焦点
<input className="focus-visible:ring-2 focus-visible:ring-ring" />
```

## 🌓 明暗模式

```tsx
// 始终使用语义化颜色（自动适配）
<div className="bg-background text-foreground">

// 只在特定模式下应用
<div className="dark:bg-black dark:text-white">

// 条件样式
<div className="bg-white dark:bg-black">
```

## 📱 响应式

```tsx
// 渐进式间距
<div className="px-4 md:px-6 lg:px-8">

// 响应式显示
<div className="hidden md:block">  // 移动端隐藏
<div className="block md:hidden">  // 只在移动端显示

// 响应式网格
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
```

## 🎨 图标

```tsx
import { IconName } from "lucide-react";

// 尺寸
<IconName className="h-3 w-3" />  // 12px
<IconName className="h-4 w-4" />  // 16px (推荐)
<IconName className="h-5 w-5" />  // 20px
<IconName className="h-6 w-6" />  // 24px

// 带文字
<Button>
  <IconName className="mr-2 h-4 w-4" />
  按钮
</Button>
```

## ⚠️ 常见错误

### ❌ 不要硬编码颜色

```tsx
// 错误
<div className="bg-white text-black border-gray-200">

// 正确
<div className="bg-background text-foreground border-border">
```

### ❌ 不要用 emoji 做图标

```tsx
// 错误
<span>📁 文件夹</span>

// 正确
<Folder className="h-4 w-4" /> 文件夹
```

### ❌ 不要在浅色模式用过度透明

```tsx
// 错误
<div className="bg-white/10">  // 看不见

// 正确
<div className="bg-white/80">  // 或用 bg-card
```

## 🔧 常用代码片段

### 居中容器

```tsx
<div className="flex min-h-screen items-center justify-center">
  <div className="w-full max-w-md">
    {/* 内容 */}
  </div>
</div>
```

### 卡片网格

```tsx
<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
  {items.map((item) => (
    <Card key={item.id} className="border-border bg-card">
      <CardContent className="p-4">
        {/* 内容 */}
      </CardContent>
    </Card>
  ))}
</div>
```

### 加载骨架

```tsx
<div className="animate-pulse space-y-3">
  <div className="h-4 bg-muted rounded w-3/4"></div>
  <div className="h-4 bg-muted rounded w-1/2"></div>
  <div className="h-4 bg-muted rounded w-5/6"></div>
</div>
```

### 空状态

```tsx
<div className="flex flex-col items-center justify-center py-12">
  <div className="rounded-full bg-muted p-4">
    <Icon className="h-8 w-8 text-muted-foreground" />
  </div>
  <p className="mt-4 text-muted-foreground">暂无内容</p>
</div>
```

### 错误提示

```tsx
<div className="rounded-lg bg-destructive/10 border border-destructive/20 p-4">
  <p className="text-sm text-destructive">{error}</p>
</div>
```

---

💡 **提示**: 将此文件加入浏览器书签，方便随时查阅！
