# AR1 文档同步覆盖审计

日期：2026-09-26。范围：SledTrace 当前 agent-reference checkout 中受 Agent 路线调整影响的全部文档。
“全部相关”不等于修改每个文件，也不等于改写历史发布；本记录说明每类去向。
本轮不修改另一仓库 MAMR，不同步覆盖其他工作树，不更改产品代码、版本、数据库或发行包。

## 所有活跃入口

| 文档 | 本轮处理 / 所属事实 |
| --- | --- |
| AGENTS.md | 调整定位与 Agent 护栏；P1–P7、证据类别、跨仓库门槛 |
| README.md | 当前已实现边界、后续诊断/比较方向及案例入口；不宣传待做能力 |
| CONTRIBUTING.md | 更正已发布 tool 能力；切片、比例验证、证据区分 |
| ai-context/CURRENT_TASK.md | AR1 文档片与 P1 下一候选；旧任务记录保留并标为历史 |
| ai-context/AI_HANDOFF.md | 当前快照、MAMR 限制、候选状态；修正过期下一步与版本冲突 |
| ai-context/NEXT_AGENT_BRIEF.md | 新接手顺序与不可误读的状态/授权 |
| ai-context/ROADMAP.md | M2.5/M3a/M3b、P1–P7 顺序、release gate；历史里程碑保留 |
| ai-context/DECISIONS.md | 追加本次采用的取舍，不抹除旧决定 |
| ai-context/DEVLOG.md | 追加已发生案例与本次文档操作/验证，计划不计作实现 |
| product/ROAD_TO_V1_0.md | 详细范围、P1–P7、D1–D3、退出门槛、预算/停止条件 |
| product/AGENT_DIRECTION_PREP.md | 固定 MAMR/PydanticAI/RAG；不重启工作流搜索 |
| product/PRODUCT_SPEC.md | v0.1 历史标记及当前路线链接，旧正文不冒充现状 |
| product/USER_ONBOARDING.md | 更正 tool/Responses 与七规则边界，计划另列 |
| architecture/SYSTEM_ARCHITECTURE.md | 当前步骤/用量事实、计划导入路径及存储前置 |
| architecture/TRACE_DATA_MODEL.md | 更正当前 span 集；未来语义不是已实现 schema |
| integrations/PYTHON_SDK_GUIDE.md | 当前 tool/result/Responses 入口，不杜撰新 API |
| demo/WARNING_RULES.md | RAG 覆盖与未来诊断区分，0 warning 非健康 |
| demo/AGENT_REPEAT_EVIDENCE.md | 保留已验证样本，取消主线等待两规则的要求 |
| demo/PYDANTIC_AI_BANK_SUPPORT.md | 固定参考职责，保留 live/stub/离线区别 |
| demo/MAMR_DIAGNOSTIC_CASE.md（新增） | 四次真实调用、posthoc 局限、无法证明的根因 |
| development/AGENT_WORKFLOW.md | 不同证据用不同测试，跨仓库与防循环约束 |
| releases/RELEASE_CHECKLIST.md | 按产品门槛验收，不按报警配额；补齐已有必要检查 |
| development/AGENT_ROADMAP_DOC_AUDIT.md（本文件） | 覆盖清单及不改理由 |

表内相对路径均以 docs/ 为起点，根目录三个入口除外。

## 已检查、无须改动的范围

- sdk/python/README.md：已准确说明发布的 tool/result、显式 Responses、估价与 source-checkout serve；
  不把路线图塞入包说明，未修改 package metadata，故本轮无需构建分发包。
- releases/V0_4_0.md 至 V0_7_1.md：不可变版本的历史说明，不回填未来 Agent 能力。
  GitHub Release / PyPI 已发行 README 不在本次仓库文档改动内。
- REBRANDING.md：名称/import/env 兼容窗口未变。
- product/V0_3_DIAGNOSTIC_INTELLIGENCE.md、ai-context/REAL_LOCAL_RAG_MILESTONE.md、
  architecture/LOCAL_RETRIEVAL_BASELINE.md：版本/阶段历史或专用 RAG 设计，不替代新路线。
- demo/SMOKE_TEST.md、REFERENCE_RAG_APP.md、LOCAL_RAG_DEMO.md、
  EXTERNAL_FEDERALIST_RAG.md、DASHBOARD_POLISH.md、local_rag_demo/README.md：
  既有 RAG/安装/视觉验收流程仍保留，不改成 Agent 能力证明。
- .agents/skills 两项工作流与 .github/copilot-instructions.md：
  已以 AGENTS/CURRENT_TASK 为权威，强调单片、比例验证、未知/兼容/安全和不自动进入下一片，无须复制新路线。
- .github issue/PR 模板：通用复现/验收/兼容/发布门槛仍适用，无 Agent 能力承诺。
- 示例 policy/corpus Markdown：测试输入不是产品文档，不为路线变动修改测试数据。
- README screenshots：本轮未改 UI，不重截或虚构新功能截图。

## 验证原则与限制

只检查文档、链接目标/锚点、授权/实现状态一致性、slice scope/docs profile 和 diff hygiene。
本机案例仅只读回读，未重跑 meeting；历史测试/费用不是本轮新验证。
不查询/改变远端 PR、不 commit/push/merge/release。最终本轮命令结果记录在 DEVLOG。
