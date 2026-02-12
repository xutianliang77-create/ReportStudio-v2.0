# 模块实现蓝图（14 模块）

## 1. Ingest Engine
- 输入：CSV/XLSX/JSON/Markdown/粘贴表格
- 输出：标准化 Dataset + Schema + 质量报告
- 关键实现：格式识别、编码检测、字段推断、质量校验、清洗、join、append

## 2. Metrics Engine
- 输入：Dataset + DSL
- 输出：指标结果集 + 口径说明 + 依赖图
- 关键实现：DSL 解析与校验、拓扑排序、除零保护、缓存策略

## 3. Analysis Engine
- 输入：指标结果集
- 输出：groupby/pivot/topn/贡献度/异常/对比矩阵
- 关键实现：统一请求结构与可复用分析算子

## 4. Insight Engine
- 输入：分析结果 + 指标上下文
- 输出：关键发现、归因、预测、可操作建议
- 关键实现：评分排序 + 模板生成 + LLM 润色 + 下钻反馈闭环

## 5. Chart Engine
- 输入：分析结果
- 输出：推荐图表、渲染配置、静态与交互图
- 关键实现：决策矩阵、样式主题、异常标注叠加

## 6. Layout Engine
- 输入：图表与指标结果
- 输出：报表区块布局与模板实例
- 关键实现：默认七段结构、区块注册、参数映射

## 7. Preview Studio
- 输入：布局快照
- 输出：可视化预览与编辑会话
- 关键实现：编辑模式、参数面板、撤销重做、自动暂存

## 8. Export Engine
- 输入：报表快照
- 输出：PDF/XLSX/DOCX/PPTX
- 关键实现：多格式导出路由、命名规则、水印、签名下载

## 9. Collaboration Engine
- 输入：报表版本与评论行为
- 输出：评论线程、评审状态、活动流
- 关键实现：评审状态机、批注定位、通知联动

## 10. Scheduler Engine
- 输入：调度规则与订阅配置
- 输出：周期执行记录、分发结果
- 关键实现：cron、失败重试、渠道分发、执行日志

## 11. Version Control
- 输入：编辑与导出动作
- 输出：版本快照、Diff、回滚结果
- 关键实现：不可变快照、差异比较、复制式回滚

## 12. Lineage Tracker
- 输入：Dataset/指标/区块/版本变更事件
- 输出：上游血缘、下游影响、健康报告
- 关键实现：DAG、增量更新、断链检测

## 13. Workspace & ACL
- 输入：成员、角色、资源权限
- 输出：访问判定、行级过滤、脱敏结果
- 关键实现：RBAC、row filter、field masking、审计

## 14. Artifact Store
- 存储策略：
  - 元数据：SQLite/PostgreSQL
  - 数据集：Parquet
  - 导出物：文件系统/S3
  - 版本快照：JSON
