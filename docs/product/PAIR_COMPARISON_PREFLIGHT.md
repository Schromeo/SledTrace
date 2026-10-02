# P5A — 配对比较证据预审

日期：2026-09-29。**P5A 预审完成，随后用户批准 P5B；其只读比较已本地实现。**
本页保留预审依据和当时提案；实现契约/用法以 [PAIR_EVIDENCE](../integrations/PAIR_EVIDENCE.md)
为准。后文“待批准”描述提案时状态，不是新的审批要求或新增采集保证。
执行状态见 [CURRENT_TASK](../ai-context/CURRENT_TASK.md)，阶段边界见
[通往 1.0 的细纲](ROAD_TO_V1_0.md)。不改变 P4 → P5 → P6 顺序。

## 1. 这次核对到了什么

核对当前 MAMR `lib/meeting-diagnostic-export.ts`、SledTrace 严格导入器、
Python 示例/任务结果 API、Dashboard 用量/价格/时间工具，并只读查询现有
4320 隔离样例库的四条记录；没有运行新会议、模型或修改源应用。

| 证据 | 可复用 | 不能推出 |
| --- | --- | --- |
| 普通 MAMR diagnostic-v1 | 尝试身份、调用/提供商/校验状态、用量来源、流程中断、人工决定 | 输入、模型、完整控制配置、应用版本、质量标准或因果关系 |
| MAMR taskResult | memoPresent、humanDecision、qualityEvaluation=not_evaluated | 有 memo/人工同意就是正确；不同 room 是同题前后版本 |
| Python 示例 metadata | task_id、variant、部分 app_version/upstream_commit | 同题同输入同配置；live 与 TestModel 是受控修复实验 |
| log_task_result | 调用方明确写入的 task_result/accepted | 使用了同一版本质量标准或经过独立语义评估 |
| 现有账本/价格/时间 | 已观测 LLM 调用、已知用量小计、覆盖缺口、受限估价、明确时间 | 全工作流捕获完整、提供商账单、由 room 时间推算执行耗时 |

隔离库是一个 RAG 样例和三个 MAMR 离线样例，不是用户全部历史记录。
三个 MAMR 记录的 input/output 为空、duration_ms 为 null，质量未评估；
此前为并列展示而调整的合成 room ID 不构成真实 baseline/candidate。
脚本化成功/业务失败/恢复案例也不是同输入单一改动的效果证据。

结论：现有源数据足以做 P4 的失败解释，不足以自行建立受控配对。
相似名称、task_id 相等、warning 减少、token 更少都不能填补缺口。

## 2. 选择最短路径，而不是先扩采集系统

| 选项 | 代价与边界 | 本轮判断 |
| --- | --- | --- |
| 直接扩 MAMR/SDK 源 metadata | 新源契约、跨仓实现、隐私与兼容验证；严格 v1 不接受额外字段 | 不作为 P5B 前置条件 |
| 根据名称/room/结果自动配对 | 无法控制输入、配置或质量混杂 | 不采用 |
| 只读双 trace + 有版本的人工比较声明 | 新的有限本地文件契约；来源必须显式标记，不能升级成源头事实 | 推荐，待批准 |

P5B 只调用已有 `GET /api/traces` 和 `GET /api/traces/{id}`。
复用当前页面、用量账本、P4 解释与证据导航，不加后端接口、表、SDK API
或 MAMR 字段。声明只在当前浏览器页面内存中；刷新/离开后重新选择，
不写 SQLite/localStorage，不下载或执行引用内容。

这是一个人工核对辅助工具，不是自动实验验证器。将来有源头配对证据时
再独立审议映射；不能因 JSON 能放进 generic metadata 就绕过语义契约。

## 3. 待批准的最小声明契约

建议 kind=`sledtrace-pair-evidence`，schemaVersion=1，最大 16 KiB，
精确两条不同且可读取的 trace；拒绝未知版本、额外字段、非法类型与超限。
固定 provenance=`user_declared`，不允许伪装成 provider/source_verified。
每个引用/标识最长 200 字符，仅有限不透明标识，不接受任意正文或可执行内容。
实现前还需将精确字符集合和错误行为写入契约测试，而非宽松自动转型。

示意（尚不能导入）：

```json
{
  "schemaVersion": 1,
  "kind": "sledtrace-pair-evidence",
  "provenance": "user_declared",
  "interventionId": "turn-envelope-fix-v1",
  "baseline": {
    "traceId": "trace_fixture_before",
    "caseId": "decision-case-1",
    "inputRef": "input-v1",
    "controlConfigRef": "controls-v1",
    "criteriaVersion": "meeting-quality-v1",
    "appVersion": "before",
    "qualityStatus": "not_evaluated",
    "qualityEvidenceRef": null
  },
  "candidate": {
    "traceId": "trace_fixture_after",
    "caseId": "decision-case-1",
    "inputRef": "input-v1",
    "controlConfigRef": "controls-v1",
    "criteriaVersion": "meeting-quality-v1",
    "appVersion": "after",
    "qualityStatus": "not_evaluated",
    "qualityEvidenceRef": null
  }
}
```

- traceId 必须非空且不同；interventionId 指明本次唯一预期代码改动。
  首片只覆盖代码修复比较，不声称支持模型/温度/工具策略同时变更的实验。
- caseId/inputRef/controlConfigRef/criteriaVersion/appVersion 可显式 null：
  表示未知；两边 null 不算一致。缺少必需键属于坏文件，而非自动补证据。
- inputRef 指同一份固定输入；controlConfigRef 由使用者核对同一模型、提供商、
  提示/数据版本、工具、输出上限、恢复策略等非干预条件。不可取得的随机因素
  和运行噪声仍是局限；相同字符串/哈希不是配置独立验证或匿名化证明。
- appVersion 应标识不同代码版本，改变项由 interventionId 解释；相同版本
  或未知版本不能声称验证了代码修复。版本引用不会触发读取仓库或执行代码。
- qualityStatus 仅 passed/failed/not_evaluated。passed/failed 要求非空
  qualityEvidenceRef，指向使用者已核对的评估记录；not_evaluated 要求 null。
  页面不自动取得该记录或验证评估正确性。criteriaVersion 标识同一验收标准及版本，
  不能用“完成了”“没有报警”代替。源头质量状态和人工评估永远分栏显示。
- 不放任务正文、prompt/response、API key、客户资料或完整配置。引用本身也可能
  敏感，文件需使用者检查；“metadata-only”不是无秘密认证。

这里的评估声明只是可审阅的人工证据索引，不是 judge 服务或语义准确率。
P6 才能用真实固定任务和实际评估记录判断改动；离线造 passed 不满足 M3b。

## 4. 页面和判断规则

一个比较视图：顶部配对条件/缺口 → 两侧结果与失败层 → 已观测用量/调用/
时间/估价 → 各自原 trace/receipt。能回答“哪里变了、还能不能判断”，
不建实验列表、调度器、排行榜、图表系统或通用 DAG。

配对判定优先级：

1. 非法文件、自配对、记录不存在、Collector 离线各有明确错误；不显示假零。
2. case/input/控制配置/验收标准任一已知不一致：**不可比**，列出原因。
3. 任一控制条件未知，或代码版本缺失/未区分：**证据不足**。
4. 条件全部按声明匹配且版本不同：**人工声明条件匹配，未独立验证**。
   不是“受控实验已证实”。两个运行只支持个案描述，不支持统计推广。

源结果与人工质量独立：源 completed、memoPresent、humanDecision、accepted
仍按各自含义显示，不替换为 qualityStatus。条件匹配时基线 passed/候选 failed
标记人工评估显示回归，不能因便宜而推荐保留；任一质量未评估则不下改进结论。
两次均 passed 也只表示人工评价符合标准，是否保留由人决定。

计量底线：

- 显示已观测 LLM 调用数；失败/取消/未终止的已记录尝试不得过滤。未知整段
  或导入缺失不虚构调用，但醒目标明；1/1 用量覆盖不是全工作流捕获完整。
- 已知 token 小计附 covered/observed 和冲突状态。部分覆盖可两侧查看，
  不算全 run 差额。只在声明条件匹配、两侧所有已观测调用口径已知兼容且
  无冲突时给**已记录调用的绝对差额**，仍不称全工作流节省。
- provider 总量与 visible-output 不合并；不猜 reasoning/cache；来源口径不同
  不算 token 差额。MAMR 缺模型不估价。
- 估价复用现有支持范围；所有已观测调用都可计价且币种/快照/口径一致才
  给对应范围差额。价格日期和“非账单”常驻。任一未知不能当免费。
- 时间只用各 trace 的明确执行时长；MAMR room 更新间隔和 span 求和都不
  替代墙钟。任一未知不算差额。真实已知零保留；第一片不提供百分比。
- 即使数字可计算，质量/控制条件不足时也不写“更高效”或“修复成功”。

## 5. P5B 执行卡与停止条件（待批准）

- 价值：用户并排查两个版本，看到可比条件、失败层、人工质量与计量缺口。
- 最小交付：严格声明解析/纯比较模型 + 现有 Dashboard 内一个只读视图。
- 预算：一片 1–2 个专注开发日；如需要新增源字段/数据库才能交付，停止并
  报告，不顺手跨仓或延长为采集平台。
- 测试：声明匹配/不同任务/不同输入/不同配置/不同标准/双 null/同版本/自配对；
  质量下降但更便宜/未评估/真实零/部分覆盖/冲突/provider-visible 混合；
  不同价格口径/未知时长/保留失败尝试/旧记录/缺记录/离线/坏文件。
- 固定离线样例只验证解析、判断和 UI，不作为真实修复结论。不新增付费会议
  或第三个框架；复用 MAMR、Python 和 RAG 边界。
- 验收：Dashboard 完整测试和 build、slice scope/check/diff；实际双记录页、
  缺口与回归状态、键盘/返回原证据、旧 RAG 回读及实际截图。
- 停止：本地可审阅候选 + DEVLOG/CURRENT_TASK/ROADMAP 同步。未经新的
  授权不提交/推送/合并/发布，不开始 P6；P6 的真实修复/评估/费用另定。

## 6. 预审验收边界

本轮仅文档和证据核对，用 docs 验证 profile，不重跑 Go/npm/SDK 构建。
当前功能代码没有变化。P3B/P4 的旧测试结果不算本轮新测试；既有工作树
仍包含其未提交的前置变更。P5B 的契约与实施必须等用户明确批准。
