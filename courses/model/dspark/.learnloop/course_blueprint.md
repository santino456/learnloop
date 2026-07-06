# Course Blueprint: DeepSeek DSpark 技术解读

## Course Promise

学完本课程后，你能够解释 DSpark 的半自回归投机解码架构与置信度调度验证机制，并基于延迟、吞吐、任务类型和成本判断它是否适合你的生产推理场景。

## Learner Job

```text
When the learner finishes this course, they can ...
```

完成课程后，学习者可以：

1. 说明 LLM 自回归推理的瓶颈，以及投机解码为何能加速而不损失质量。
2. 解释早期投机解码（Speculative Sampling / Speculative Decoding）的核心算法、接受规则和局限。
3. 对比自回归 draft（Eagle3）与并行 draft（DFlash）的权衡，并解释 DSpark 的半自回归设计如何缓解 suffix decay。
4. 解释 confidence head、前缀生存概率和 hardware-aware prefix scheduler 的工作方式。
5. 描述 DeepSpec 训练流程、target cache 成本、以及 vLLM/SGLang 部署方式。
6. 根据 workload 特征和硬件条件，判断何时引入 DSpark、何时维持基线。

## Experience Standard

每个 section 只要求学习者做一件事：

- understand a mechanism（理解一个机制）
- compare two choices（对比两个选择）
- verify a claim from evidence（根据证据验证一个断言）
- practice a move（练习一个可检查的动作）
- make a judgment（在权衡中做出判断）

如果某个 section 只是让学习者读一段文字，就重新设计它。

## Proposed Modules

| Module | Form | Learner action | Sources | Components |
|--------|------|----------------|---------|------------|
| m0 | Tutorial | 理解投机解码的历史、核心算法与早期局限 | speculative-sampling, speculative-decoding, dspark-paper §2 | concept, compare, evidence, exercise, timeline |
| m1 | Tutorial | 理解投机解码动机与 DSpark 定位 | dspark-paper, deepspec-repo | concept, compare, evidence, exercise |
| m2 | Tutorial | 理解半自回归 draft 架构 | dspark-paper | concept, compare, evidence, exercise |
| m3 | Reference | 查阅置信度调度验证的算法与公式 | dspark-paper | evidence, concept, exercise |
| m4 | Reference | 查阅训练流程与部署事实 | deepspec-repo, marktechpost-dspark, hf-weights | concept, evidence, exercise |
| m5 | Perspective | 判断是否应在生产中采用 DSpark | dspark-paper, deepspec-repo | compare, decision, evidence |

## Section Blueprint

| Section id | Learner action | Evidence needed | Component |
|------------|----------------|-----------------|-----------|
| m0-why-history | understand | 课程设计决策 | concept |
| m0-problem | understand | dspark-paper §1, §2 | concept |
| m0-speculative-sampling | understand / verify | speculative-sampling paper | evidence, concept |
| m0-speculative-decoding | understand / compare | speculative-decoding paper, dspark-paper §2 | evidence, concept, compare |
| m0-limitations | understand | 课程设计决策 | concept |
| m0-timeline | understand | 多篇论文 | timeline |
| m0-exercise | practice | m0 内容 | exercise |
| m1-bottleneck | understand | dspark-paper §1, §2 | concept |
| m1-spec-decoding | understand | dspark-paper §2 | concept |
| m1-dspark-intro | compare / verify | dspark-paper §1, deepspec-repo | evidence, compare |
| m1-prerequisites | understand | 课程设计决策 | concept |
| m1-exercise | practice | m1 内容 | exercise |
| m2-paradigms | compare | dspark-paper §2, eagle3-paper, dflash-paper | compare, concept |
| m2-sar-arch | understand | dspark-paper §3.1 | concept, flow |
| m2-sequential-head | understand | dspark-paper §3.1 | concept, evidence |
| m2-exercise | practice | m2 内容 | exercise |
| m3-problem | understand | dspark-paper §3.2 | concept |
| m3-confidence-head | understand | dspark-paper §3.2 | concept |
| m3-scheduler | understand | dspark-paper §3.2 | concept |
| m3-training-objective | look up | dspark-paper §3.3 | evidence |
| m3-exercise | practice | m3 内容 | exercise |
| m4-deepspec | look up | deepspec-repo README | concept, evidence |
| m4-training | look up | dspark-paper §4, marktechpost-dspark | concept, evidence |
| m4-checkpoints | look up | hf-weights | concept |
| m4-deployment | look up | deepspec-repo, vllm-issues | concept, evidence |
| m4-exercise | practice | m4 内容 | exercise |
| m5-offline-results | verify | dspark-paper §5.1 | evidence |
| m5-production-results | verify | dspark-paper §5.2 | evidence |
| m5-compare-methods | compare | dspark-paper §5, mtp-paper | compare |
| m5-limitations | judge | dspark-paper §5, §6 | concept |
| m5-decision | judge | 全课程 verified claims | decision |

## Open Questions

- 是否需要增加一节动手实验，让读者用 DeepSpec 复现一个最小评估？
- vLLM/SGLang 的 DSpark 集成状态变化很快，哪些命令应该标记为 `needs-human-review`？
- 课程中涉及的 38 TB target cache 是 Qwen3-4B 设置下的数字，是否需要在不同模型尺寸间给出换算提示？
