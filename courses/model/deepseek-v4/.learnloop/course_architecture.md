# Course Architecture: DeepSeek-V4 系列论文解读

## Course Promise

学完本课程后，学习者能够解释 DeepSeek-V4 系列的核心架构选择（CSA/HCA、mHC、Muon），理解其在百万 token 长上下文下的效率优势，并能根据任务需求在 V4-Pro 与 V4-Flash 之间做出合理选择。

## Proposed Modules

| Module | Form | Learning job | Sources | Components |
|--------|------|--------------|---------|------------|
| m1 | Tutorial | 建立长上下文效率问题的整体认知 | DeepSeek-V4 论文 | figure |
| m2 | Tutorial | 梳理 V4 相对 V3 的继承与三大升级 | DeepSeek-V4 论文 | table |
| m3 | Tutorial | 理解 mHC 的流形约束与 Sinkhorn 投影 | DeepSeek-V4 论文 | flow |
| m4 | Tutorial | 掌握 CSA 的压缩、索引与 MQA | DeepSeek-V4 论文 | flow |
| m5 | Tutorial | 对比 HCA/CSA 与混合配置，理解工程细节 | DeepSeek-V4 论文 | table, figure |
| m6 | Tutorial | 理解 Muon 正交化更新与 V4 的稳定性处理 | DeepSeek-V4 论文 | decision |
| m7 | Reference | 概览训练与推理基础设施的关键优化 | DeepSeek-V4 论文 | table, flow |
| m8 | Perspective | 综合评估结果并做出模型选型判断 | DeepSeek-V4 论文 | decision, table |

## Open Questions

- 是否需要补充官方技术博客或开源实现链接来支撑某些细节？
- 是否需要为 CSA/HCA 增加示意图（目前依赖论文 PDF 中的 Figure 3/4）？
- 长上下文评估中的具体 benchmark 名称是否需要在 Reference 模块中展开？
