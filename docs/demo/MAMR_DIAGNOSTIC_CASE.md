# MAMR：真实中断案例与取证边界

日期：2026-09-26（America/Los_Angeles；事后映射的 UTC 时间为 2026-09-27）。
本记录整理本次会话中已发生的浏览器运行；文档同步阶段只回读现有 Collector 记录与应用代码，没有重跑模型。

## 运行与授权

Multi-AI-MeetingRoom（MAMR）是用户已有的多 LLM 会议应用，本次是内部 dogfooding，
不是独立外部采用，也没有观察到工具型 Agent 执行。未核定公开许可，不把它称为开源参考框架。

用户授权一次会议，费用上限 $0.50，允许 Unlimited 输出配置。
两个 seat：Anthropic claude-haiku-4-5-20251001（Strategist）与 OpenAI gpt-4.1-nano（Critical Reviewer）。
一轮、turn_by_turn，第三 seat 与 Observer 关闭。任务使用合成/公开产品事实，讨论优先改善首次 Connection/双 seat 设置还是增加 workflow pack。
这次授权不构成未来永久额度；停止后未重试、未恢复、未生成 synthesis/memo。

| 顺序 | 阶段 / 模型 | UI output tokens | UI reported latency | 应用估算 USD | 结果 |
| --- | --- | ---: | ---: | ---: | --- |
| 1 | proposal / Haiku | 561 | 6.6 s | 0.0068 | 完成 |
| 2 | proposal / nano | 277 | 3.6 s | 0.0022 | 完成 |
| 3 | review / Haiku | 668 | 8.0 s | 0.0120 | 完成 |
| 4 | review / nano | 188 | 3.8 s | 0.0038 | 格式校验失败 |

合计 UI output 为 1694，逐次 latency 之和约 22 s（不是会议墙钟耗时），
应用估算之和约 $0.0248（非真实账单，也不证明完整实际费用低于授权上限）。
MAMR 估价采用 provider 默认配置，不能据此声称按选定模型官网费率准确计价。
不从这些四舍五入的金额反推 input tokens。Unlimited 不代表无 provider/应用限制。

## 直接观察与能定位到的层级

UI 错误：“This seat returned an invalid Turn Envelope: The turn statement or card is invalid.”
会议在可恢复边界暂停，并显示恢复入口；尚无最终 memo，也没有人工质量否定。

MAMR 源码路径（相对其仓库）：

- lib/meeting-state.ts 的 parseTurnEnvelope：JSON 解析和顶层字段检查之后，
  合并检查 statement 的字符串/长度以及 card 是否对象；失败返回上述 message。
- app/api/discuss/route.ts 的 runAgent：streamProvider 返回后进行此校验；
  agent.format_error 只发 id/message/usage，随后抛 TurnFormatError。
- app/page.tsx 的 agent.delta/agent.format_error 处理没有在这个失败记录中保留完整无效输出。
- UsageSummary 本有 inputTokens/outputTokens/estimatedUsd/latencyMs，但事后 UI 抄录没有完整字段。

因此可定位到**应用输出合同校验层**，而不是据此证明 provider HTTP 失败或非法 JSON。
无法从现存证据分辨究竟是 statement 缺失/类型/空值/过长，还是 card 类型不符；
也不能证明截断、模型能力不足或哪个 prompt 导致了它。不得为找回丢失证据无限付费复现。

## 已写入 SledTrace 的记录

本机 trace ID：trace_cf3d673b401d4df290cfeaa85ab49c74。
本机回读端点：GET /api/traces/trace_cf3d673b401d4df290cfeaa85ab49c74；
本机记录不是仓库中的可移植 fixture，服务或数据库变化后可能不可用。

- 名称 MAMR live meeting - posthoc UI mapping；4 个 llm spans，trace error，0 现有 RAG warnings。
- sample_kind=real_provider_posthoc_ui_mapping；agent_tool_execution=false。
- input/total tokens 未知，output 取自 UI；source_status、phase 和 reported_* 在 metadata。
- 原始调用时间未知，span timing 未测量；trace duration_ms=0 只是快速映射耗时，不是会议耗时。
- accepted=false 是当时粗粒度中断映射，不是人工拒绝回答。保留原记录，明确此解释限制；
  未来需分别表达 contract failure、workflow interrupted、quality not evaluated、recovery available。
- 0 warnings 不说明任务正常；当前 Collector 没有解释此类 Agent/合同失败的 D1–D3 规则。

## 对后续工作的约束

1. P1 先给出安全结构化校验原因，不先改 prompt/model/validator 接受范围。
2. P2 在源头记录调用、合同、流程、任务四层事实，来源与计量完整性分开。
3. P3 脱敏 bundle 保真导入前解决必要的原子保存/重复语义。
4. P4/P5 展示失败定位与结果约束比较；P6 才据证据修改一次应用。
5. 成功 live 可以验证采集链；失败分支用离线 fixture。没有新理由不追着同一随机失败跑。
6. 保留 PydanticAI 正常重复反例和现有 RAG 回归；不把这个多 LLM 会议冒充工具 Agent 样本。

详细步骤与停止规则见 [通往 1.0](../product/ROAD_TO_V1_0.md)；
此记录是历史证据，新增能力仍以 [当前任务](../ai-context/CURRENT_TASK.md) 为准。
