# P6C0 — 归并失败的最小安全原因码取证提案

日期：2026-09-29。状态：**已审阅的提案，待用户批准；尚未实现任何新契约。**
执行入口：[CURRENT_TASK](../ai-context/CURRENT_TASK.md)。保持
[P6 固定任务/质量与停止条件](P6_EXPERIMENT_PREFLIGHT.md)。本轮无产品源代码
改动、跨仓写入、模型调用或发布。

## 1. 不再重复随机失败测试

已确认的丢失点（MAMR HEAD `eabf737a2197366c283a6c5e99c755264f023c5a`，干净）：

1. `lib/meeting-state.ts` 的 `ReductionResult.error.code` 已有
   `invalid_event`、`invalid_envelope`、`unknown_reference`、`state_limit`。
2. `app/api/discuss/route.ts` 的 `reduceCompletedTurns` 发出
   `agent.reduction_error` 时只带 message/envelope/usage，不带原因码。
3. `app/page.tsx` 将服务端失败或客户端自身归并失败只保存为 reductionError
   字符串；`lib/meeting-record.ts` 的严格读取也只保留这项字符串。
4. `lib/meeting-diagnostic-export.ts` 只导出 `reductionFailureObserved`。
5. 定向讨论的 delta 数量预检查也发 `agent.reduction_error`，**不是 reducer**。

旧真实记录没有失败 JSON 正文或 reducer 详情；评估明确指出不可推断原因。
这些源码事实证明诊断信息丢失的位置，不证明当时是 unknown_reference 或
state_limit。不会从未知 Claim 字符串/错误消息自动解析原因码，不复制私有创作。

## 2. 选最小有信息增益的改动

| 路径 | 判断 |
| --- | --- |
| 整个会议反复付费重跑 | 不采用：仍可能丢信息，没有新授权或受控根因 |
| 手工提供本机脱敏的旧错误 | 若用户已有可直接使用；目前没有，不强制用户翻日志 |
| 解析已有 reductionError 文本 | 不采用：文本不是契约，含任意信息，来源关卡也不明确 |
| 原生 gate + 原因码一路保留 | 推荐：已有类型码，有限字段，零付费离线先验收 |

用途是决定下一次应检查**哪个应用分支**；不是自动修复、概率打分或模型归责。
不会改 parser 接受范围、提示词、模型、token/超时额度、恢复/重试规则。

## 3. 拟批准的精确契约

### 一个可选本地诊断对象

新来源仅普通 Decide 的现有失败事件/记录，不扩 Plan/Review/Observer/Solo。
`agent.reduction_error` 增加可选对象 `reductionDiagnostic`；对应 transcript
item 的可选字段允许对象或 null（明确不可归属的诊断）：

```json
{"version":1,"gate":"server_reducer","code":"unknown_reference"}
```

仅以下组合允许；对象精确三个键，不允许任意 text/details/extra 字段：

| gate | 允许 code | 捕获点 |
| --- | --- | --- |
| server_reducer | invalid_event / invalid_envelope / unknown_reference / state_limit | 服务端实际 ReductionResult.error.code |
| client_reducer | 同上四个固定码 | 客户端实际 ReductionResult.error.code |
| targeted_delta | targeted_delta_limit | 现有定向回复数量限制预检查 |

这第五个码是拟新增的固定 precheck 标签，**不是现有 reducer 的第五个分支**。
不得从模型返回、任意异常 message 或文本正则生成这些码。旧事件不带字段时
照旧处理，旧记录照旧读；已缺失的原因保持未知，不回填、不重写历史错误。
同 turn 冲突诊断不得 last-write-wins：保留原事件历史/原记录，明确本地
采集冲突，当前投影将该字段置为 sticky null（后续重复消息不恢复成某个码）。
严格记录读取保留 null；v2 对该项输出 null，不再导出单一原因码。旧字段缺省
也导出 null；两者都表示原因无法确定，不声称远端能区分未采集与冲突。
不能以另一原因静默覆盖；没有字段不代表关卡成功。

### 导出 v2，而非在 v1 偷塞字段

- 原 `schemaVersion=1` 格式/导出能力保持不变；新增明确标注版本的 v2 选择，
  不悄悄让旧下载按钮输出另一个格式。消费者接通前不改默认路径。
- v2 沿用 kind `mamr-ordinary-meeting-diagnostic` 和原 allowlist；每个 turn
  **新增一个必需键** `reductionDiagnostic`，值为 null 或上面的精确对象。
- 旧/未捕获、冲突或未失败 turn 取 null；bool=true 但原因缺失也取 null，标未知。
  不由 status=done/false 构造 passed 证据。本版不增加成功采集事件或完整率承诺。
- 非 null 只允许 `reductionFailureObserved=true` 且 status=error；违反时拒绝
  新导出/导入，不能静默丢字段或默认为某个原因码。格式失败信号独立保留。
- 既有 turn/seat/phase/round 与 receipt 身份规则不变。gate 是捕获位置，
  不是父子因果关系；同一 turn 涉及多个尝试则不将 turn 码臆配给某一个调用。
- Export 全新显式投影；不复用原 MeetingRecord 序列化、不包含原 error.message、
  envelope、模型原输出、statement、prompt、Memo、Claim ID、未知键或秘密。

### SledTrace 严格分版本接收

- 复用 `POST /api/imports/mamr`：v1 按原契约，v2 按上面精确新增字段；不做
  全局 unknown-fields 宽容，也不把 v2 伪装成 v1。未知版本拒绝且不保存。
- 存储 source 明确 `mamr_diagnostic_v2`，保留原 v2 bundle；旧 v1 provenance
  不改写。复用原子保存，无 SDK API 或数据库表迁移。
- 同 room ID 的 trace 身份**继续相同**：相同映射 payload no-op，不同内容
  （包括同 room v1→v2）继续 409，不覆盖旧记录。需要核对新版时用独立隔离库，
  不改 room ID 造第二次执行、不做隐式“升级导入”。
- 界面按 source/version 选择严格读法，显示关卡及 source-reported code，
  精确返回原 turn/receipt。旧记录继续未知；格式校验、归并/定向预检查、
  call/provider、workflow/human decision 和 quality 各自保留。

## 4. 两片实施，不混成业务修复

**P6C1：MAMR 源取证（最多 1 日，待批准）。** 遵守该仓 Correction Brief，
修改普通会议事件类型、两个服务端失败发射点、客户端失败映射/本机归并点、
严格 transcript 读取与 allowlisted v2 导出/版本选择。补离线 fixtures，
`pnpm.cmd check` 和真实本机保存/恢复/导出 UI 验收，更新英语与中文镜像。
不改业务接受/提示词/重试，不运行付费会议，收口后停止。

**P6C2：SledTrace 读取（最多 1 日，后续选择）。** 分版本 parser + source
投影 + 已有解释卡；Go 测试、Dashboard tests/build、真实导入/精确导航/
旧记录回读。使用中性离线例子；不复制私有会议正文，不改原记录做“成功图”。

最低验收矩阵：

- 四个实际 reducer 分支与 targeted_delta 分开；服务端/客户端来源不能混淆；
- 新失败事件→保存→读取→导出→导入，精确码不丢；没有新增调用或双计 usage；
- 旧记录/null、不带诊断的旧事件、started-only 仍读，未知不补成功/零；
- 未知 code/gate、错 gate-code 组合、额外/重复键、矛盾 bool/status/version、
  重复冲突诊断与歧义身份明确拒绝或降级，不能制造精确关联；
- 含假秘密/正文/Claim 文本的记录经过 export 后，诊断 JSON、SledTrace
  数据库和界面均不含这些内容；投影失败不回退发送原记录；
- v1 fixture、旧 RAG、同内容 no-op、同 room 不同内容 409、事务失败保持；
- UI 将 unknown_reference 指向引用集合/渲染上下文核对，将 state_limit
  指向状态预算核对，但不自动认定“模型幻觉”或“应该扩大容量”。

只记录原因类别不会复原旧失败，也不会立即证明缺陷来自源代码。
下一次有真实原因码仍需用允许的本机结构和固定上下文重放，再挑单一补丁。
不能为收口把离线测例当成真实修复/M3b。若两片预算超时交具体阻碍，
不扩通用 JS SDK、Telemetry、框架、raw-output 收集或另一个采集平台。

## 5. 本次需要的授权

请批准**上述有限跨仓修改及 event/local-record/export-v2/import-v2 契约**。
实施按 P6C1→P6C2 分片收口，范围仅本地离线；费用额度为零。
批准不授权应用修复、真实模型调用、commit/push、合并、tag 或发布。
若不批准，则保留 P6B 的“失败已知、原因未知”，延期原因采集；不再原地审计。
