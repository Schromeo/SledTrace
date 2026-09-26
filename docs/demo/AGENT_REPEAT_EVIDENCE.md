# E4P — Agent 重复行为的离线证据基线

这是一组**手写、合成、无费用**的规则设计样本，不是已发布的 Agent
警告、真实模型调用、真实开发者浪费案例或诊断准确率评估。`llm` 步骤由
脚本记录，`model=scripted-fixture-no-provider`；没有模型请求，token
用量应显示 Unknown。成功样本只记录脚本任务结果，不写
`accepted=true`；失败样本明确记录 `accepted=false`。两者都不表示
回答质量已经评审。工具调用也由脚本记录，不执行外部动作。

从 `sdk/python` 运行：

```powershell
$env:OPENAI_API_KEY=$null
python -B -m examples.agent_repeat_evidence all
```

已有本地 Collector 时可显式添加
`--collector-url http://127.0.0.1:4319 --flush`，然后在 Dashboard
选择 `e4-repeat-evidence-*`。该命令不需要 PydanticAI 或 OpenAI 密钥。

| 样本 | 人工标签 | 为什么不是自动结论 |
| --- | --- | --- |
| `same_result_stable` | 疑似重复结果 | 相同工具、参数键、结果键与已知状态版本；仍未证明第二次调用可删除。 |
| `polling_changed_state` | 正常轮询 | 参数相同，但从 pending 变为 complete，状态版本也改变。 |
| `confirmation_unknown_state` | 不可判断 | 参数与结果键相同，外部状态未知；必要确认不能被假定为浪费。 |
| `repeat_error_stable` | 疑似重复失败 | 相同错误类别、参数键和已知状态版本；任务失败，不据此计算浪费金额。 |
| `retry_recovered` | 正常恢复 | 首次超时，第二次成功；不是连续相同失败。 |
| `corrected_parameter` | 正常修正 | 失败后更换参数，第二次成功。 |

`fixture_comparison` 中的键是人工编写的**合成标签**，不是从真实参数或
结果计算的散列，也不是 SledTrace 对外承诺的元数据字段。不能认为把
私密原文做一次哈希就自动安全。当前 Collector 对这六条无检索 trace
仍返回 0 条 RAG 警告；“0 条”只说明现有规则未触发，**不是六个 Agent
行为都正常**。页面里的步骤和错误状态是观察事实，上表标签是预先给定
的试验假设。

2026-09-26 本地读取与页面核对（隔离 Collector；以下是**修正后**的
记录，按 trace ID 区分同名的早期试验记录）：

| 样本 | trace ID | 状态 / spans / 警告 |
| --- | --- | --- |
| `same_result_stable` | `trace_517c13f203484d25b399d023c8994db9` | ok / 3 / 0 |
| `polling_changed_state` | `trace_7fd20bdce0664d93b4930d530a968719` | ok / 3 / 0 |
| `confirmation_unknown_state` | `trace_ba0959d7c02f4e3f93a9f944dfcf4857` | ok / 3 / 0 |
| `repeat_error_stable` | `trace_36661c9eee6a47a28d1f828cbb5c1195` | error / 3 / 0 |
| `retry_recovered` | `trace_62ff32bc77cf4b29960df926521bc814` | ok / 3 / 0 |
| `corrected_parameter` | `trace_f6f11b17df9a4783b6f60bceca8af0c4` | ok / 3 / 0 |

页面可见脚本 LLM 用量 `0/1`、Known subtotal Unknown、调用耗时 Not
measured；成功样本不显示“Acceptance: passed”。`same_result_stable`
的工具详情显示两次相同的合成比较键；
`repeat_error_stable` 显示两个失败工具步骤与失败任务；正常轮询与状态
未知的反例也分别可打开。页面不会自动显示上述“疑似”标签为 warning。
第一次页面验收发现成功样本的 `accepted=true` 会被渲染成
“Acceptance: passed”，因此已从成功样本移除；早期六条本地 trace
保留作修正过程记录，不应当作最终样本。

参考工作流 A1 的自然反例：固定版本 PydanticAI bank-support 成功 trace
`trace_53efb0fcf50c4f75bc634c1a17d094da` 中，`customer_name_lookup`
出现两次，因为上游动态 instructions 在第二次模型步骤再次读取姓名。
这是一个**真实执行的工具重复**，却不能仅凭名称重复称作浪费；该模型
步骤为离线 TestModel，不是真实 provider 调用。

2026-09-26 E4R 把这个反例变成可核对的**执行观察**，不是新规则：
默认离线 `balance` run 的第二次姓名查询在进程内比较实际 ID 和返回值，
只记录 `same_customer_id=true`、`same_return_value=true`、第一次调用的
`previous_span_id`，以及 `dynamic_instructions_reevaluated` 的上下文。
示例的 SQLite 在建表后只读，故 `fixture_state` 明确限于这个合成内存
fixture。原始 ID 和姓名不进入这组比较元数据；它不是通用指纹格式，
也没有自动证明第二次调用是浪费。新离线 trace
`trace_10e071d881fd4fef8ab4a4cc843eded8` 经 Collector 回读为 ok、
5 spans、0 现有 RAG 警告；Dashboard 的第二个 `customer_name_lookup`
详情显示前一个 span 引用与上述布尔值，LLM 用量仍是 Unknown `0/2`。
单次成功的公开参考示例仍不能替代用户工作流、正例或留出集。

下一门槛：这六个手写样本还没有达到 E4 每条约 8–12 个正反/边界样本、
留出测试集与真实用户场景的要求。先判断接入是否能提供安全、可信的
参数/结果可比性与状态证据，再决定是否实现第一条保守提示。缺字段时
保持不可判断，不扩大为语义裁判或通用 Agent runtime。
