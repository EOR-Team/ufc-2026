# 工作流状态切换系统测试指南

## 系统概述

已成功实现四状态工作流系统，包含：

1. **collecting_conditions** - 收集用户症状
2. **collecting_requirements** - 收集个性化需求
3. **selecting_clinic** - 自动选择诊室
4. **patching_route** - 优化路线

## 文件结构

### 新增文件
```
src/types/workflow.js           # 类型定义（JSDoc）
src/utils/route.js              # 路径处理工具函数
src/stores/api.js              # API服务层
src/stores/workflow.js         # 工作流状态管理
src/stores/index.js            # Store导出索引
.env.development              # 开发环境配置
.env                         # 通用环境配置
TEST_WORKFLOW.md             # 测试指南（本文件）
```

### 修改文件
```
src/views/NavigationView.vue  # 主页面集成工作流逻辑
```

## 测试步骤

### 1. 启动前端
```bash
cd frontend
npm run dev
```

访问：http://localhost:5173/nav_page

### 2. 预期行为

#### 阶段1：症状收集
- 页面加载后自动显示："你好！我是智能寻路助手，可以帮你导航到医院各个科室。请描述你的症状，以便我为你选择合适的诊室。"
- 状态指示器显示："正在收集症状"
- 输入框提示："请描述你的症状（例如：头痛、发烧、咳嗽等）..."

**测试输入：** "我头痛已经两天了，有点发烧，感觉头晕"

#### 阶段2：自动诊室选择
- 系统调用 `/api/triager/collect_conditions/` API
- 状态指示器变为："正在选择诊室"
- 显示："已分析你的症状：[...]。现在为你选择合适的诊室..."

#### 阶段3：需求收集
- 系统调用 `/api/triager/select_clinic/` API
- 状态指示器变为："正在收集需求"
- 显示："已为你选择 [诊室ID] 诊室。请告诉我你有什么个性化需求..."
- 输入框提示："请描述你的个性化需求（例如：需要轮椅、优先就诊、避开人群等）..."

**测试输入：** "我需要轮椅，希望避开人群多的区域"

#### 阶段4：路线优化
- 系统调用 `/api/triager/collect_requirement/` API
- 状态指示器变为："正在优化路线"
- 显示："已记录你的需求。现在根据诊室和需求优化路线..."
- 系统调用 `/api/triager/patch_route/` API

#### 阶段5：完成
- 状态指示器变为："路线规划完成"
- 显示优化后的路线
- 显示"重新开始"按钮

### 3. 错误处理测试

#### 网络错误
- 关闭后端服务器
- 尝试输入症状
- 应显示错误消息和状态指示器变为"出现错误"

#### 重启工作流
- 在错误状态或完成状态输入"重新开始"或点击"重新开始"按钮
- 工作流应重置到初始状态

### 4. API端点映射

前端API调用与后端端点对应关系：

| 前端方法 | 后端端点 | 描述 |
|---------|---------|------|
| `collectConditions` | `POST /api/triager/collect_conditions/` | 收集症状 |
| `selectClinic` | `POST /api/triager/select_clinic/` | 选择诊室 |
| `collectRequirement` | `POST /api/triager/collect_requirement/` | 收集需求 |
| `patchRoute` | `POST /api/triager/patch_route/` | 修改路线 |
| `getRoutePatch` | `POST /api/triager/get_route_patch/` | 完整工作流 |

### 5. 数据流验证

#### 基底路径定义
```javascript
[
  { this: 'entrance', next: 'registration_center' },
  { this: 'registration_center', next: '<xxx_clinic>' },
  { this: '<xxx_clinic>', next: 'pharmacy' },
  { this: 'pharmacy', next: 'exit' }
]
```

#### 路径处理流程
1. **生成原路径**：用实际`clinic_id`替换`<xxx_clinic>`
2. **应用补丁**：使用`patches`数组修改原路径
3. **验证连续性**：确保修改后路径连接正确
4. **格式化显示**：转换为用户友好的文本格式

### 6. 状态机验证

工作流状态机包含7个状态：

| 状态 | 描述 | UI表现 |
|------|------|--------|
| `idle` | 初始状态 | 显示开始按钮 |
| `collecting_conditions` | 收集症状 | 显示症状输入框 |
| `selecting_clinic` | 选择诊室 | 自动处理，显示加载 |
| `collecting_requirements` | 收集需求 | 显示需求输入框 |
| `patching_route` | 优化路线 | 自动处理，显示加载 |
| `completed` | 完成 | 显示最终路线 |
| `error` | 错误 | 显示错误信息 |

### 7. 视觉反馈

#### 状态指示器颜色
- 空闲：灰色
- 收集症状：蓝色
- 选择诊室：黄色
- 收集需求：紫色
- 优化路线：绿色
- 完成：深绿色
- 错误：红色

#### 加载指示器
- API调用期间显示三个跳动圆点
- 消息显示"正在处理..."状态

#### 输入控制
- API处理期间禁用输入框和发送按钮
- 根据状态显示不同的输入提示

## 已知限制

1. **后端依赖**：需要后端API服务器运行在 http://localhost:8000
2. **语音集成**：语音输入功能需要额外的语音识别服务集成
3. **错误恢复**：网络错误后需要手动重启工作流

## 故障排除

### 常见问题

#### 1. API调用失败
- 检查后端是否运行：`curl http://localhost:8000/api/triager/collect_conditions/`
- 检查网络连接
- 查看浏览器控制台错误

#### 2. 状态转换卡住
- 检查工作流store的状态机逻辑
- 验证API响应格式是否符合预期
- 查看开发者工具中的网络请求和响应

#### 3. 路径显示错误
- 验证`BASE_PATH`定义是否与后端匹配
- 检查`generateOriginalRoute`函数
- 测试`applyPatchesToRoute`函数

#### 4. UI显示问题
- 检查Tailwind CSS类是否正确应用
- 验证响应式布局
- 测试不同屏幕尺寸

## 性能考虑

1. **消息历史**：工作流store管理所有消息，可能影响长时间使用
2. **API调用**：多个连续API调用，需要合理处理加载状态
3. **状态管理**：Pinia store提供高效的状态管理和响应式更新

## 扩展建议

1. **本地存储**：添加localStorage支持保存工作流状态
2. **语音输入**：集成现有的语音交互组件
3. **离线模式**：添加模拟API响应支持离线测试
4. **多语言**：扩展支持多语言界面
5. **进度保存**：允许用户中断后恢复工作流

## 总结

工作流状态切换系统已完全实现，具有：

✅ **完整的状态机**：7个状态，自动转换
✅ **API集成**：与后端智能分诊API完全集成
✅ **路径处理**：基底路径生成、补丁应用、验证
✅ **用户界面**：状态指示、加载反馈、错误处理
✅ **类型安全**：JSDoc类型定义确保数据一致性
✅ **关注点分离**：Store、组件、工具函数分离清晰

系统已准备好进行端到端测试和集成测试。