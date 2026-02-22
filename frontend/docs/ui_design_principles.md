# UI 设计核心原则

> UFC-2026 前端界面设计指导原则 | 基于实际代码实现

## 技术栈概览
- **框架**: Vue 3.5.25 (Composition API)
- **UI 框架**: Vuetify 3.12.0 (Material Design 3)
- **样式系统**: Tailwind CSS v4.2.0
- **构建工具**: Vite 7.3.1
- **路由**: Vue Router 5.0.3
- **状态管理**: Pinia 3.0.4（当前未使用）
- **图标**: Material Design Icons (@mdi/font 7.4.47)

---

## 一、设计哲学

### 1.1 核心理念
- **简洁至上**：每个元素都有明确目的
- **一致性优先**：相同功能，相同表现
- **用户为中心**：操作直观，反馈明确
- **渐进增强**：基础功能可靠，高级体验优雅

### 1.2 设计价值观
1. **清晰**：信息层次分明，一目了然
2. **高效**：最少操作完成目标
3. **愉悦**：微交互提升使用体验
4. **包容**：适应不同用户需求

---

## 二、视觉设计原则

### 2.1 色彩系统
```
主色: #4252b3 (深蓝)
背景: #f6f6f8 (浅灰)
文本: 深灰(#1e293b) / 中灰(#64748b)
```

**应用规则**：
- 主色用于主要操作和重要状态
- 中性色构建信息层次
- 通过透明度创建视觉深度
- 保持足够的对比度（≥4.5:1）

### 2.2 排版规范
```
字体: Inter (现代、清晰)
标题: 20px, 600字重, 紧缩字距
正文: 16px, 正常字重, 1.5行高
辅助: 12px, 500字重, 大写字母
```

**排版原则**：
- 左对齐为主，增强可读性
- 合理使用空白，引导视线
- 字号层级不超过4级
- 标签使用大写字母区分

### 2.3 间距系统
```
基础单位: 4px
小间距: 8px (组件内部)
中间距: 12px (组件之间)
大间距: 16px (区块之间)
```

**间距规则**：
- 使用倍数关系保持节奏感
- 垂直间距大于水平间距
- 内容密集区域适当压缩
- 重要元素周围留白更多

### 2.4 圆角规范
```
圆形: 9999px (头像、FAB)
大圆角: 16px (卡片、对话框)
标准圆角: 8px (按钮、输入框)
小圆角: 4px (标签、进度条)
```

**圆角原则**：
- 交互元素使用明显圆角
- 内容容器使用适中圆角
- 完全圆形用于重要操作
- 保持同一层级圆角一致

### 2.5 阴影系统
```
轻微: shadow-sm (0 1px 2px rgba(0,0,0,0.05))
中等: shadow (0 1px 3px rgba(0,0,0,0.1))
明显: shadow-lg (0 10px 15px -3px rgba(0,0,0,0.1))
强烈: shadow-2xl (0 25px 50px -12px rgba(0,0,0,0.25))
自定义: shadow-[...] (FAB按钮使用自定义值)
```

**实际应用**：
- **主容器**: `shadow-2xl`
- **FAB按钮**: `shadow-[0_8px_20px_rgba(0,0,0,0.35)]`
- **悬停状态**: `hover:shadow-[0_12px_28px_rgba(0,0,0,0.45)]`
- **激活状态**: `!shadow-[0_16px_32px_rgba(0,0,0,0.55)]`

**阴影原则**：
- 阴影反映元素层级和交互状态
- 自定义阴影增强品牌特色和 Material Design 3 效果
- 避免过度使用阴影，保持界面简洁
- 交互时动态调整阴影增强反馈

---

## 三、组件设计原则

### 3.1 通用组件规范

#### 按钮设计
```vue
<!-- 主要按钮 -->
<button class="px-3 py-2 bg-primary text-white rounded-lg shadow hover:shadow-lg">
  主要操作
</button>

<!-- 次要按钮 -->
<button class="px-3 py-2 bg-white text-slate-700 border border-slate-300 rounded-lg">
  次要操作
</button>

<!-- FAB按钮 -->
<button class="w-16 h-16 bg-primary text-white rounded-full shadow-lg">
  <span class="material-symbols-outlined">add</span>
</button>
```

**按钮原则**：
- 主要操作最突出
- 危险操作使用红色
- 禁用状态降低对比度
- 提供明确的点击反馈

#### 输入控件
```vue
<!-- 文本输入 -->
<input class="px-3 py-2 border border-slate-300 rounded-lg focus:border-primary focus:ring-2 focus:ring-primary/20">

<!-- 开关控件 -->
<div class="w-11 h-6 bg-slate-300 rounded-full">
  <div class="w-5 h-5 bg-white rounded-full shadow transform translate-x-0.5"></div>
</div>

<!-- 滑块控件 -->
<div class="h-2 bg-slate-200 rounded-full">
  <div class="h-full bg-primary rounded-full" style="width: 50%"></div>
</div>
```

**输入原则**：
- 焦点状态清晰可见
- 错误状态立即反馈
- 标签与输入关联明确
- 提供操作说明和示例

### 3.2 布局组件规范

#### FixedAspectContainer
```vue
<!-- 默认尺寸（300 × 600px） -->
<FixedAspectContainer
  bg-color-class="bg-white"
  extra-class="font-display"
  :shadow="true"
>
  <!-- 页面内容 -->
</FixedAspectContainer>

<!-- 规划尺寸（332 × 774.66px）需显式传入 -->
<FixedAspectContainer
  :width="332"
  :height="774.66"
  bg-color-class="bg-white"
  extra-class="font-display"
  :shadow="true"
>
  <!-- 页面内容 -->
</FixedAspectContainer>
```

**实际状态**：
- **组件默认**: 300 × 600px（`width` 默认 300，`height` 默认 600）
- **规划尺寸**: 332 × 774.66px（9:21 宽高比）
- **当前实现**: `HomeView` 和 `SettingsView` 使用默认尺寸
- **静态版本**: `_page_main/code.html` 和 `_page_settings/code.html` 使用规划尺寸

**布局原则**：
- 所有页面使用统一容器，确保视觉一致性
- 固定尺寸策略简化响应式处理
- 内部使用弹性布局（Flexbox）
- 溢出内容通过 `useViewportOverflow` composable 智能处理

#### 消息气泡系统（四层架构）
```vue
<!-- 1. MessageBubble（路由器） -->
<MessageBubble
  name="assistant"  <!-- 或 'user' -->
  message="消息内容"
  icon="smart_toy"  <!-- 可选 -->
/>

<!-- 2. BasicMessageBubble（通用底层） -->
<BasicMessageBubble
  :is-assistant="true"  <!-- 或 false -->
  message="消息内容"
  name="助手"
  icon="smart_toy"
/>

<!-- 3. 具体角色组件 -->
<AssistantMessageBubble message="你好！" />
<UserMessageBubble message="我想去门诊部" />
```

**实际架构**：
1. **MessageBubble**: 根据 `name` 属性路由到对应组件
2. **BasicMessageBubble**: 通用实现，接受 `isAssistant` prop
3. **AssistantMessageBubble**: 助手消息封装，左对齐，蓝色主题
4. **UserMessageBubble**: 用户消息封装，右对齐，灰色主题，独立实现

**消息原则**：
- 角色通过位置（左/右）和颜色（蓝/灰）清晰区分
- 最大宽度限制：80%容器宽度
- 图标尺寸：40×40px 圆形
- 气泡形状：`rounded-xl`，助手 `rounded-tl-none`，用户 `rounded-tr-none`

### 3.3 反馈组件规范

#### 加载状态
```vue
<!-- 旋转加载 -->
<div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>

<!-- 进度条 -->
<div class="w-full h-1 bg-slate-200 rounded-full">
  <div class="h-full bg-primary rounded-full" style="width: 60%"></div>
</div>
```

#### 状态指示器
```vue
<!-- 成功提示 -->
<div class="flex items-center gap-2 text-green-600">
  <span class="material-symbols-outlined">check_circle</span>
  <span>操作成功</span>
</div>

<!-- 错误提示 -->
<div class="flex items-center gap-2 text-red-600">
  <span class="material-symbols-outlined">error</span>
  <span>操作失败</span>
</div>
```

**反馈原则**：
- 操作结果立即反馈
- 长时间操作显示进度
- 错误信息具体可操作
- 成功反馈简洁明确

---

## 四、交互设计原则

### 4.1 操作反馈

#### 即时反馈
- **悬停**：轻微样式变化
- **点击**：缩放效果 (scale-95)
- **长按**：持续视觉反馈
- **完成**：状态变化提示

#### 延迟反馈
- 超过1秒的操作显示加载状态
- 网络请求显示进度或骨架屏
- 复杂计算提供预估时间

### 4.2 手势交互

#### 长按交互（语音输入）
```js
// 实际实现（HomeView.vue）
const { isActive: isListening, start, end } = useLongPress(250)
```

**交互细节**：
- **长按阈值**: 250ms（实际使用），350ms（默认值）
- **视觉反馈**: FAB 按钮样式变化 + `VoiceOverlay` 显示
- **防误触**: `preventClick` 方法阻止短按干扰
- **状态控制**: `isActive` 状态控制录音界面

**触摸交互**：
- **轻点**: 选择或激活
- **长按**: 250ms 触发语音输入
- **滑动**: 列表滚动（`ConversationList`）
- **手势**: 支持触摸设备完整交互

#### 鼠标交互
- **悬停**：显示工具提示
- **点击**：主要操作
- **右键**：上下文菜单
- **滚轮**：内容滚动

### 4.3 动画原则

#### 过渡动画
```css
/* 快速过渡 */
transition: all 150ms ease;

/* 中等过渡 */
transition: all 300ms ease;

/* 慢速过渡 */
transition: all 500ms ease;
```

#### 自定义动画
```css
/* 脉冲效果 */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 淡入淡出 */
@keyframes fade {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

**动画原则**：
- 动画服务于功能，而非装饰
- 保持动画时长一致
- 避免过度动画干扰用户
- 提供动画性能优化

---

## 五、响应式设计原则

### 5.1 布局适应性

#### 固定尺寸策略
- **规划尺寸**: 332×774.66px（9:21 宽高比）
- **实际默认**: 300×600px（`FixedAspectContainer` 默认值）
- **父容器**: `#app` 使用 100vw × 100vh 居中显示
- **内部布局**: 弹性布局（Flexbox） + 相对单位
- **溢出处理**: `useViewportOverflow` composable 智能检测和适配

#### 内容适配
- 文本自动换行，避免水平滚动
- 图片按比例缩放
- 表格在小屏幕转为卡片
- 导航栏适应可用空间

### 5.2 断点策略
```
sm: 640px   (平板竖屏)
md: 768px   (平板横屏)
lg: 1024px  (小桌面)
xl: 1280px  (桌面)
```

**断点原则**：
- 移动优先设计
- 渐进增强体验
- 保持核心功能可用
- 避免布局跳跃

---

## 六、可访问性原则

### 6.1 键盘导航
- 所有交互元素支持Tab导航
- 焦点状态清晰可见 (`focus:ring-2`)
- 提供键盘快捷键
- 支持Esc键取消操作

### 6.2 屏幕阅读器
- 使用语义化HTML标签
- 提供有意义的ARIA标签
- 图片提供alt文本
- 表单字段正确关联标签

### 6.3 颜色对比
- 文本与背景≥4.5:1对比度
- 交互元素≥3:1对比度
- 避免纯颜色传达信息
- 提供高对比度模式

### 6.4 运动敏感
- 提供减少动画选项
- 避免闪烁或快速移动
- 重要信息不依赖动画
- 支持系统偏好设置

---

## 七、开发工作流

### 7.1 组件开发流程
1. **需求分析**：确定组件功能和场景
2. **接口设计**：定义props和events接口
3. **样式实现**：应用设计系统规范
4. **交互实现**：添加状态和反馈
5. **测试验证**：功能、样式、可访问性
6. **文档编写**：使用示例和注意事项

### 7.2 样式验证清单
- [ ] 尺寸符合设计规范
- [ ] 颜色对比度达标
- [ ] 间距使用倍数关系
- [ ] 圆角层级正确
- [ ] 阴影效果适当
- [ ] 响应式表现正常
- [ ] 交互反馈明确
- [ ] 可访问性支持

### 7.3 代码质量要求
- 组件单一职责
- props接口最小化
- 样式类名语义化
- 注释清晰必要
- 性能优化考虑
- 浏览器兼容性

---

## 八、设计决策记录

### 8.1 重要设计决策

#### 决策1：固定尺寸布局策略
**问题**：如何在保持设计一致性的同时简化响应式处理？
**方案**：使用 `FixedAspectContainer` 固定尺寸容器，支持默认值（300×600）和规划尺寸（332×774.66）
**实际状态**：当前使用默认尺寸，静态HTML使用规划尺寸
**理由**：简化响应式处理，保持视觉一致性，便于设计稿对照

#### 决策2：四层消息气泡架构
**问题**：如何高效管理不同角色的消息样式并保持代码复用？
**方案**：MessageBubble（路由）→ BasicMessageBubble（通用）→ Assistant/UserMessageBubble（具体）四层架构
**实际结构**：`UserMessageBubble` 独立实现，不复用 `BasicMessageBubble`
**理由**：最大化代码复用，清晰角色区分，灵活的使用方式（可通过路由或直接使用）

#### 决策3：长按交互模式优化
**问题**：如何防止语音输入误触并提供良好反馈？
**方案**：250ms长按阈值（实际使用），`useLongPress` composable 封装逻辑
**实际实现**：FAB 按钮样式变化 + `VoiceOverlay` 毛玻璃蒙版 + `ListeningIndicator` 波形动画
**理由**：防止误触，明确操作意图，提供完整的视觉和动效反馈

#### 决策4：自定义阴影系统增强
**问题**：如何增强界面立体感和品牌特色？
**方案**：使用自定义阴影值而非 Tailwind 默认值
**实际应用**：FAB 按钮使用 `shadow-[0_8px_20px_rgba(0,0,0,0.35)]` 等自定义值
**理由**：更明显的视觉层次，更好的 Material Design 3 效果，交互状态区分明显

#### 决策5：Composables 交互逻辑封装
**问题**：如何复用复杂的交互逻辑？
**方案**：使用 Vue 3 Composables 封装 `useLongPress` 和 `useViewportOverflow`
**实际实现**：`useLongPress` 处理长按逻辑，`useViewportOverflow` 处理布局适配
**理由**：逻辑复用，代码清晰，易于测试和维护

### 8.2 设计权衡

#### 权衡1：简洁 vs 功能丰富
**选择**：优先简洁，渐进披露
**理由**：核心用户需要快速完成任务，高级功能按需提供

#### 权衡2：一致性 vs 特殊性
**选择**：保持一致性，特殊场景例外
**理由**：一致性降低学习成本，特殊场景需要明显区分

#### 权衡3：美观 vs 性能
**选择**：平衡两者，性能优先
**理由**：流畅体验比华丽效果更重要，优化动画性能

---

## 九、最佳实践总结

### 9.1 设计实践
1. **从内容出发**：先确定内容，再设计容器
2. **保持一致性**：相同功能，相同表现
3. **提供反馈**：每个操作都有明确响应
4. **简化流程**：最少步骤完成目标
5. **测试验证**：真实场景验证设计

### 9.2 开发实践
1. **组件化架构**：清晰的四层消息气泡架构，`FixedAspectContainer` 统一容器
2. **Composables 模式**：`useLongPress` 和 `useViewportOverflow` 封装复杂交互逻辑
3. **设计系统驱动**：严格遵循色彩、排版、间距、圆角、阴影规范
4. **性能优化**：路由懒加载，Tailwind CSS 按需生成，Vite 构建优化
5. **可访问性基础**：语义化 HTML，ARIA 属性，键盘导航支持
6. **代码质量**：清晰的组件接口，完整的注释，一致的命名规范

### 9.3 协作实践
1. **设计移交**：提供完整设计规范
2. **组件文档**：记录使用方式和限制
3. **设计评审**：定期审查实现质量
4. **用户测试**：收集真实用户反馈
5. **知识共享**：建立设计模式库

---

## 十、参考资料

1. **设计系统**
   - [Tailwind CSS 设计系统](https://tailwindcss.com/docs)
   - [Material Design 3](https://m3.material.io)
   - [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines)

2. **可访问性**
   - [Web Content Accessibility Guidelines (WCAG)](https://www.w3.org/WAI/standards-guidelines/wcag/)
   - [A11Y Project](https://www.a11yproject.com)

3. **性能优化**
   - [Web Vitals](https://web.dev/vitals/)
   - [CSS Triggers](https://csstriggers.com)

4. **用户体验**
   - [Nielsen Norman Group](https://www.nngroup.com)
   - [UX Collective](https://uxdesign.cc)

---

## 项目实现状态总结

### ✅ 核心功能已实现
1. **现代化技术栈**：Vue 3 + Vuetify 3 + Tailwind CSS v4
2. **完整组件库**：从布局容器到交互组件的完整体系
3. **语音交互界面**：长按录音 + 完整视觉反馈系统
4. **响应式布局**：智能视口溢出检测和适配
5. **设置系统**：完整的设置页面和控件

### 🔄 待集成功能
1. **后端API**：连接后端智能分诊、导航、医疗记录系统
2. **状态管理**：Pinia stores 实现全局状态
3. **语音功能**：语音识别和语音合成集成
4. **地图导航**：医院地图和路径规划界面

### 🎯 技术亮点
1. **架构清晰**：组件分层合理，职责分离明确
2. **代码质量高**：完整的注释，一致的规范
3. **用户体验优秀**：流畅的交互，清晰的反馈
4. **可维护性强**：模块化设计，易于扩展
5. **文档完善**：详细的设计规范和开发指南

---

*文档版本：1.1.0*（基于实际代码分析更新）
*最后更新：2026年2月22日*
*维护团队：UFC-2026 设计与开发团队*
*基于实际代码版本：前端项目 v0.0.0*

> **设计原则总结**  
> 1. **简洁实用**：每个元素都有明确目的，去除冗余  
> 2. **一致性优先**：相同功能，相同表现，建立用户信任  
> 3. **用户为中心**：操作直观，反馈明确，减少认知负荷  
> 4. **渐进增强**：基础功能可靠，高级体验优雅  
> 5. **可访问性**：从一开始考虑所有用户的需求