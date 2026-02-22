# UI 设计美学规范与原则

> UFC-2026 前端界面设计系统 | 基于 Vue 3 + Tailwind CSS + Material Design

---

## 设计哲学

### 核心理念
- **简洁实用**：去除冗余，聚焦核心功能
- **一致性**：跨页面、跨组件的统一体验
- **可访问性**：清晰的信息层次和交互反馈
- **情感化设计**：通过微交互增强用户体验

### 设计原则
1. **内容优先**：界面服务于功能，不干扰用户任务
2. **渐进式披露**：按需展示信息，避免信息过载
3. **即时反馈**：所有操作都有明确的视觉或动效反馈
4. **容错设计**：允许用户撤销操作，提供安全网

---

## 视觉设计系统

### 1. 色彩系统

#### 主色调
```css
--color-primary: #4252b3;      /* 主品牌色 - 深蓝色 */
--color-background-light: #f6f6f8;  /* 浅色背景 */
--color-background-dark: #14161e;   /* 深色背景 */
```

#### 色彩应用规范
- **主色 (#4252b3)**：主要按钮、重要图标、激活状态
- **辅助色**：通过透明度调节创建层次
  - `bg-primary/10`：轻微背景强调
  - `bg-primary/20`：中等背景强调
  - `bg-primary/90`：激活状态
- **中性色**：文本、边框、背景
  - 文本：`text-slate-900` (深灰) / `text-slate-500` (中灰)
  - 边框：`border-slate-100` (浅灰) / `border-primary/20` (主色淡)
  - 背景：`bg-white` / `bg-slate-50` / `bg-slate-100`

#### 色彩对比度
- 文本与背景：≥ 4.5:1 (WCAG AA标准)
- 交互元素：≥ 3:1
- 非文本元素：≥ 3:1

### 2. 排版系统

#### 字体家族
```css
--font-display: "Inter", sans-serif;
```

#### 字号层级
| 用途 | 类名 | 大小 | 字重 | 行高 |
|------|------|------|------|------|
| 页面标题 | `text-xl` | 1.25rem (20px) | `font-semibold` | 1.2 |
| 正文内容 | `text-base` | 1rem (16px) | `font-normal` | 1.5 |
| 辅助文本 | `text-sm` | 0.875rem (14px) | `font-normal` | 1.4 |
| 标签/说明 | `text-xs` | 0.75rem (12px) | `font-medium` | 1.3 |
| 按钮文字 | `text-[10px]` | 0.625rem (10px) | `font-medium` | 1.2 |

#### 字距与对齐
- **字距**：`tracking-tight` (标题) / `tracking-normal` (正文)
- **大写字母**：`uppercase` + `tracking-wider` (标签)
- **对齐**：左对齐为主，特定场景右对齐

### 3. 间距系统

#### 基础间距单位
- **基础单位**：0.25rem (4px)
- **常用间距**：
  - 微小间距：`gap-1` (4px)
  - 小间距：`gap-2` (8px) / `gap-3` (12px)
  - 中间距：`gap-4` (16px)
  - 大间距：`gap-6` (24px)

#### 内边距规范
| 组件类型 | 水平内边距 | 垂直内边距 | 类名 |
|----------|------------|------------|------|
| 按钮 | `px-3` (12px) | `py-2` (8px) | 中等按钮 |
| 卡片 | `px-3` (12px) | `py-3` (12px) | 内容容器 |
| 消息气泡 | `px-3` (12px) | `py-2` (8px) | 对话内容 |
| 设置项 | `p-3` (12px) | `p-3` (12px) | 列表项 |

#### 外边距规范
- 组件间：`mt-2 mb-2` (垂直8px)
- 区块间：`mb-3` (底部12px)
- 页面边距：`ml-3 mr-3` (水平12px)

### 4. 圆角系统

#### 圆角层级
```css
border-radius: {
  "DEFAULT": "0.5rem",    /* 8px - 标准圆角 */
  "lg": "1rem",           /* 16px - 大圆角 */
  "xl": "1.5rem",         /* 24px - 超大圆角 */
  "full": "9999px"        /* 完全圆形 */
}
```

#### 应用场景
- **完全圆形**：头像、FAB按钮、开关滑块
- **大圆角**：卡片、对话框、消息气泡
- **标准圆角**：按钮、输入框、标签
- **小圆角**：进度条、分割线

### 5. 阴影系统

#### 阴影层级
| 层级 | 类名 | 效果 | 应用场景 |
|------|------|------|----------|
| 轻微 | `shadow-sm` | 0 1px 2px 0 rgba(0,0,0,0.05) | 卡片、列表项 |
| 中等 | `shadow` | 0 1px 3px 0 rgba(0,0,0,0.1) | 按钮、输入框 |
| 明显 | `shadow-lg` | 0 10px 15px -3px rgba(0,0,0,0.1) | 模态框、FAB按钮 |
| 强烈 | `shadow-2xl` | 0 25px 50px -12px rgba(0,0,0,0.25) | 主容器、重要卡片 |
| 自定义 | `shadow-[...]` | 自定义值 | 特殊效果 |

#### 交互阴影
- **悬停**：`hover:shadow-lg` / `hover:shadow-[0_15px_35px_rgba(0,0,0,0.4)]`
- **激活**：`active:scale-95` + 阴影增强
- **长按**：阴影增强 + 透明度变化

---

## 组件设计规范

### 1. 布局容器

#### FixedAspectContainer
```vue
<FixedAspectContainer 
  width="332"
  :height="774.66"
  bg-color-class="bg-white"
  extra-class="font-display"
  :shadow="true"
>
```

**规范**：
- 所有页面使用固定尺寸：332 × 774.66px (9:21)
- 统一ID：`id="main-display-block"`
- 背景：`bg-white` + `shadow-2xl`
- 溢出控制：`overflow-y: auto` (内部滚动)

### 2. 消息气泡系统

#### 三层架构
1. **BasicMessageBubble**：基础组件，最小props接口
2. **AssistantMessageBubble**：助手专用，蓝色主题，左对齐
3. **UserMessageBubble**：用户专用，灰色主题，右对齐

#### 设计规范
- **最大宽度**：80%容器宽度
- **间距**：`mt-2 mb-2 ml-3 mr-3`
- **图标**：40×40px圆形，背景色区分角色
- **名称标签**：`text-xs` + `uppercase` + `tracking-wider`
- **气泡形状**：圆角矩形，对话方向指示

### 3. 交互按钮

#### FAB (Floating Action Button)
```vue
<button class="relative flex flex-col items-center justify-center w-20 h-20 rounded-full text-white shadow-[0_10px_25px_rgba(0,0,0,0.3)]">
  <span class="material-symbols-outlined text-3xl mb-1">mic</span>
  <span class="text-[10px] font-medium text-white/90">长按说话</span>
</button>
```

**规范**：
- 尺寸：80×80px完全圆形
- 布局：垂直居中，图标+文字
- 阴影：多层自定义阴影增强立体感
- 交互：长按350ms触发，提供视觉反馈

### 4. 状态指示器

#### ListeningIndicator
- **背景**：透明背景，浮动覆盖
- **动画**：脉冲环 + 音频波形
- **定位**：绝对定位，`z-20`层级
- **触发**：长按FAB显示，释放隐藏

### 5. 设置界面组件

#### 开关控件
```vue
<div class="toggle-track" :class="{ 'bg-primary': isActive }">
  <div class="toggle-thumb" :class="{ 'translate-x-5': isActive }"></div>
</div>
```

#### 滑块控件
```vue
<div class="relative h-2 bg-slate-200 rounded-full">
  <div class="absolute h-full bg-primary rounded-full" :style="{ width: value + '%' }"></div>
  <div class="absolute left-[50%] -translate-x-1/2 w-4 h-4 bg-white border-2 border-primary rounded-full shadow-md"></div>
</div>
```

---

## 动效设计规范

### 1. 过渡动画

#### 基础过渡
```css
transition-all: 所有属性过渡
transition-colors: 颜色过渡
transition-transform: 变换过渡
```

#### 持续时间
- 快速：150ms (悬停、点击)
- 中等：300ms (页面切换、模态框)
- 慢速：500ms (复杂动画、状态变化)

### 2. 自定义动画

#### 脉冲环动画
```css
@keyframes pulse-ring {
  0%   { transform: scale(0.8); opacity: 0.5; }
  50%  { transform: scale(1.2); opacity: 0.3; }
  100% { transform: scale(0.8); opacity: 0.5; }
}
```

#### 音频波形动画
```css
@keyframes wave-flow {
  0%   { height: 20px; }
  50%  { height: 80px; }
  100% { height: 20px; }
}
```

### 3. 交互反馈

#### 按钮反馈
- **悬停**：阴影增强，背景微变
- **点击**：`active:scale-95` 缩小效果
- **长按**：持续视觉反馈，状态变化

#### 状态变化
- 显示/隐藏：淡入淡出 + 缩放
- 加载状态：旋转或脉冲动画
- 成功/错误：颜色变化 + 图标动画

---

## 响应式设计

### 1. 布局适应性

#### 固定尺寸策略
- 主容器：固定332×774.66px
- 父容器：100vw × 100vh居中显示
- 内部内容：相对单位 + 弹性布局

#### 溢出处理
- 垂直内容：`overflow-y: auto` + 隐藏滚动条
- 水平内容：`overflow-x: hidden`
- 长文本：自动换行，最大宽度限制

### 2. 暗色模式支持

#### 颜色变量
```css
text-slate-900 dark:text-slate-100
bg-white dark:bg-background-dark
border-slate-100 dark:border-slate-800
```

#### 切换策略
- 基于系统偏好或用户设置
- 平滑过渡，保持对比度
- 图标和图片适配

---

## 可访问性规范

### 1. 键盘导航
- 所有交互元素支持Tab导航
- 焦点状态清晰可见
- 快捷键支持（如Esc关闭）

### 2. 屏幕阅读器
- 语义化HTML结构
- ARIA标签和属性
- 有意义的alt文本

### 3. 颜色对比
- 文本与背景≥4.5:1
- 交互元素≥3:1
- 避免纯颜色依赖

---

## 开发工作流

### 1. 组件创建流程
1. 分析需求，确定组件类型
2. 设计props接口，保持一致性
3. 实现基础样式和功能
4. 添加交互和动效
5. 测试和验证
6. 文档化使用方式

### 2. 样式验证步骤
1. **尺寸验证**：检查容器尺寸匹配332×774.66px
2. **溢出检查**：确保内容不溢出容器
3. **响应性测试**：不同视口下的表现
4. **交互验证**：所有交互状态正常工作
5. **可访问性检查**：键盘导航和屏幕阅读器

### 3. 浏览器自动化工具使用
- `mcp_io_github_chr_evaluate_script`：检查样式和状态
- `mcp_io_github_chr_take_snapshot`：视觉验证
- 实时重载测试：确保修改立即生效

---

## 设计决策记录

### 1. 固定尺寸布局
**决策**：使用332×774.66px固定尺寸
**原因**：
- 保持设计一致性
- 简化响应式处理
- 模拟移动设备体验
- 便于设计稿对照

### 2. 三层消息气泡架构
**决策**：Basic → Assistant/User三层组件
**原因**：
- 代码复用最大化
- 角色区分清晰
- 样式维护简单
- 扩展性强

### 3. 长按交互模式
**决策**：350ms长按触发语音输入
**原因**：
- 防止误触
- 提供明确操作反馈
- 符合移动端交互习惯
- 增强用户体验

### 4. 自定义阴影系统
**决策**：使用自定义阴影值而非Tailwind默认
**原因**：
- 更明显的立体效果
- 更好的视觉层次
- 交互状态区分明显
- 品牌特色体现

---

## 最佳实践

### 1. 样式组织
- 使用Tailwind工具类为主
- 自定义CSS仅用于复杂动画
- 保持样式内联，避免全局污染
- 使用CSS变量主题化

### 2. 组件设计
- 单一职责原则
- props接口最小化
- 提供合理的默认值
- 支持完整的事件系统

### 3. 性能优化
- 减少不必要的重绘
- 合理使用CSS硬件加速
- 图片和图标优化
- 代码分割和懒加载

### 4. 维护性
- 清晰的注释和文档
- 一致的命名规范
- 版本控制和变更记录
- 定期代码审查

---

## 参考资料

1. [Tailwind CSS v4 文档](https://tailwindcss.com/docs)
2. [Material Design 3 指南](https://m3.material.io)
3. [Web Content Accessibility Guidelines (WCAG)](https://www.w3.org/WAI/standards-guidelines/wcag/)
4. [Inter 字体家族](https://fonts.google.com/specimen/Inter)
5. [Material Symbols](https://fonts.google.com/icons)

---

*最后更新：2026年2月22日*
*版本：1.0.0*
*维护者：UFC-2026 设计系统团队*