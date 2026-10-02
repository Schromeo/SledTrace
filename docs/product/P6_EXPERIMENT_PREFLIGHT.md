# P6A — 固定实验与下一片决策

日期：2026-09-29。状态：**预审完成，P6B 展示修复已本地验收；P6 的真实应用修复/效果验证未完成。**
执行入口：[CURRENT_TASK](../ai-context/CURRENT_TASK.md)。沿用
[Road to v1.0](ROAD_TO_V1_0.md) 的 P6/M3b 门槛；不新增框架、诊断配额或发布授权。

P6C0 已核对 typed 原因码在 event/本地记录链路丢失，形成
[精确取证/版本/隐私提案](P6_REDUCTION_CAPTURE_PROPOSAL.md)，尚待跨仓和契约批准。
不代表取得旧失败根因或修复应用；固定任务与人工标准不变。

## 1. 新证据和明确弃权

只读核对 MAMR 当前源码（HEAD `eabf737a2197366c283a6c5e99c755264f023c5a`，
工作树干净）、普通 Decide 的 metadata-only diagnostic-v1 及已有评估。
来源位置为另一个私有仓库的 `docs/evaluations/2026-09-27-ordinary-creative-meeting-live-001.md`
及其 `artifacts/ordinary-creative-live-001/diagnostic-v1.json`。这是本机审计定位，
不是可公开访问的链接，也不授权复制私有创意、全文 Memo、截图或输入。

确认的有限事实：一份真实运行包含 JSON 格式拒绝，以及另一次格式通过后发生的
Canonical State 归并失败；随后显式恢复并到达人工批准。正式质量仍未评估。
不搬运原任务内容，不把它当成公开 benchmark 或配对基线。

| 源头位置 | 已确认 | 不能推出 |
| --- | --- | --- |
| `runAgent` | terminal receipt 在归并之前发出，validation 只表示 Turn Envelope 校验 | passed 就是该轮被状态机采用 |
| `reduceCompletedTurns` | 后续归并失败产生独立 `agent.reduction_error`，不会产生该尝试的 `agent.done` | 提供商没返回、JSON 错误、失败一定由未知 Claim 引起 |
| diagnostic-v1 `turns` | 已有 `reductionFailureObserved` 与 `formatFailureObserved`，包含失败尝试 | reducer 详细原因、失败原值、正确修复策略 |
| SledTrace 严格导入 | 这些字段保留在原源 bundle；LLM span status 来自调用状态 | span returned 就是工作流成功 |
| P4 `mamrExplanation.ts` | 按唯一身份核对 receipt/turn，但解释未使用归并失败字段 | 本次真实应用已被修复、具有完整因果链 |

拒绝预先决定加 token、换模型、放宽 parser 或重试。旧 Sept26 posthoc 案例没有
精确失败原值；新记录也没有失败 JSON 正文和 reducer 详情。当前 parser 的
`unknown_reference` 是可能分支，不是这个真实失败的已证根因。

## 2. P6B：已本地补齐已知失败层的解释

以下是该片的固定决策/验收卡，现已本地实现；执行证据在 DEVLOG 与
[导入指南](../integrations/MAMR_DIAGNOSTIC_IMPORT.md)。不是新的待实现要求。

**用户成果：** 同一个尝试可以明确显示“提供商完成、格式通过、状态归并失败”，
并回到相应源证据。人工后来批准整个会议，不抹掉此前失败。

单一改动：只扩 SledTrace 的只读解释投影，使用已经导入的唯一匹配 turn 的
`reductionFailureObserved`；不改业务应用、不扩 v1、不新增 warning 或存储。
精确匹配不成立时保留缺口，不按顺序、名字相似或 parent 猜关联。
若同一条记录存在多种失败信号，逐项保留且不臆断优先因果。

验收清单：

- returned/completed/passed + 归并失败：显示独立应用状态关卡失败，原因未记录；
- 格式失败、调用失败、不完整提供商返回、started-only 和正常通过仍各自正确；
- 原记录里的失败尝试与恢复成功都保留；整个流程 complete/approved 与质量
  not_evaluated 分列，不合成“模型回答正确”；
- 缺失/重复/冲突 turn 或 receipt 不强行关联；不能把裸布尔值当作已知失败根因；
- 现有唯一 receipt 导航、RAG/legacy 回退、P5 配对显示不回归；
- 用**新写的中性脱敏离线测例**表示这类结构，标为 synthetic/offline，不复制
  私有内容，也不伪称为那次真实 provider 的完整重放；
- Dashboard tests/build、scope/check/diff 与实际 Collector→Dashboard UI，给截图；
  仅为修复真实证据暴露的展示缺口，不能算真实应用修复或 M3b 达标。

预算：一个有限 Dashboard 切片，最多 1 个工作日；零 API 调用。若现有身份
无法可靠关联，交付具体反例/缺口报告，不顺手改 importer/capture 契约。
停止：验收后收口，不自动实施 P6C、commit/push 或发布。

## 3. 为 P6C 固定一条公开普通任务（尚未执行）

caseId：`p6-first-run-decision-v1`；inputRef：`p6-public-input-v1`。
下列文字是这条输入的完整版本，不借用私有创作任务：

> 我们只有两名开发者、五个工作日，要为本地 Python 诊断工具选择下一项
> 首次使用工作：A，写清 SDK 与本地 runtime 的安装和启动边界；B，新增
> Agent 框架适配器。已知 SDK 已有 pip 包；现有源码启动仍需要 Go/Node；
> 尚未交付仓库外完整 runtime。禁止云托管、新认证、付费用户调研，禁止
> 把拟议功能写成已经发布。请选择一项，给五天内可执行计划、另一个选项
> 的暂缓理由、两项风险及停止条件。区分已知事实、假设和未验证信息。

这是冻结的**假设任务事实**，不是最新产品状态声明，不随版本更新改词。
任务形态 ordinary Decide，一轮、两个 Seats（Strategist / Critic）、固定
Chair 操作计划、不启用 Observer/工具/自动重试。控制模式 turn_by_turn；
保持选定有限输出 profile、每调用 caps、提供商/模型/角色/语言/超时完全一致。
基线先确定并写下具体 provider/model IDs 与全部设置再运行；目前未选定。
controlsRef 不填虚假的完整值：配置未冻结前为 null，不能宣称可比较。

版本标准 `p6-decision-quality-v1`，两侧使用同一清单，人工逐项判定：

1. 明确选择一个主工作，并说明为什么暂缓另一项；选 A/B 本身不是评分答案。
2. 对齐两人/五天约束；每一天有可执行任务和可检查产物，不只是泛泛口号。
3. 不把已有 pip SDK 等同于已交付仓库外完整产品；不声称未知适配器已可用。
4. 不引入被禁止的云/认证/付费调研；依赖与假设明确。
5. 至少两项具体风险及可操作的停止条件，保留有实质意义的未解决分歧。
6. 使用者能说明下一步如何行动，接受/拒绝及理由有明确记录。

六项全部通过才可在人工评估中记 passed；任何明确不满足记 failed；缺少
成品或评分证据保持 not_evaluated（流程失败另记），不将未知质量记成错误。
评估记录包括条目判断、对应产物位置、评分者和理由；配置在看到候选前冻结。
源 qualityEvaluation 不改写；人工判断依现有
[PAIR_EVIDENCE](../integrations/PAIR_EVIDENCE.md) 独立声明。

## 4. P6C 只在根因证据与授权齐备后启动

- 先复用已经保存的失败结构、允许的本机详细错误、实际 prompt/validator
  对照；有一个可重放具体分支和有依据的单一补丁，再请求跨仓实施授权。
  不为随机重现错误反复完整开会；没有这些证据则标记延期，而不是猜补丁。
- 如最小补丁必须扩采集/导出，则先单独审议新版本契约、隐私与迁移。
  不解析 D-069 说明性错误字符串为新公共 API，不往严格 v1 塞额外字段。
- 每个 appVersion 指 MAMR 实际 code commit，加 dirty 改动摘要/哈希（如有）；
  不把 SledTrace 展示版本当作源应用改动版本。冻结输入、control snapshot、
  标准和人工干预记录；偏离则标记不可比。
- **P6B 同一 trace 的前后 UI 不是 P5 的两次运行。** 不克隆 trace 规避
  self-pair 检查；UI 缺陷修复不能伪造 usage/cost 提升或真实 MAMR 修复。
- 真实调用需要重新批准费用、总调用次数和失败处理；本轮额度为零，历史
  $0.50 / $0.10 授权不复用。先离线，再至多一个失败阶段的有限 replay；
  同题完整 baseline/candidate 必须单独确定整个计划的预算后才调用。
- 一对运行先验证可行性；有信息增益和预算才采用原 P6 的 3 题×每版3次。
  小样本只支持这个任务/环境的工程判断，不证明通用准确率或市场价值。
- 所有失败、取消、恢复调用保留在观察范围；未上报 usage 不补零，调用耗时
  之和不是工作流墙钟时间，估价不是账单；不同口径不强算差值。

keep：使用者能由定位证据解释保留一个单一修改，契约/旧路径不退化，目标
问题改善且任务质量不下降，资源代价可接受。revert：质量回归、仅藏掉失败、
破坏协议或额外代价不值得。结果无区分/控制不齐：inconclusive，不凑成功图。
最多两轮**有新证据**的修复；同一缺口无新增证据立即结束/延期，不扩大测试。
真实定位→改动→使用者保留/撤销的闭环才可能满足 M3b；本预审不满足。

## 5. 本轮交付边界

P6A 只改变 SledTrace 的计划/交接文档；随后 P6B 已实现本仓展示修复。
两片均无源合同、MeetingRoom 改动、新采集或模型调用；P6C 仍条件化。
维持 P1→P2→P3→P4/P5→P6 主序，不以新证据为理由另建通用 Agent 平台。
此前本地未提交的代码与文档保留；发布基线仍为 v0.7.1。
