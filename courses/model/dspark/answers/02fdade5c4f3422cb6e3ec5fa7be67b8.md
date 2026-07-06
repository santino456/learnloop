---
question_id: "02fdade5c4f3422cb6e3ec5fa7be67b8"
course_id: "dspark"
module_id: "m0"
section_id: "m0-problem"
---

# Answer

用户的问题是：

> 意思是要主模型并行预测这几个 token，对内存的开销是一样，但是 GPU 的运算压力会不会是几倍？这个到底是怎么回事？

这是一个很好的工程直觉问题。答案是：**运算压力（FLOPs）确实会增加，但它不是瓶颈，所以 walltime 不会同比增加**。

类比：你从家开车去公司，堵在高速入口 20 分钟，高速上开 5 公里只要 2 分钟。现在让你多带两个人（多验证几个 token），车里坐满了，但路程没变、收费站还是那台、高速入口还是堵 20 分钟。总时间几乎一样——虽然车里人多确实“载重”变大了。

对应到 GPU：

| 开销来源 | 是否随 K 线性增长 | 为什么 |
|---|---|---|
| 权重读取（HBM → SRAM） | 否 | 权重只读一次，多 K 个 token 还是这批权重 |
| KV cache 读取 | 基本否 | 已有 cache 不用重新生成 |
| Linear 层的 FLOPs | 是（K 倍） | 激活矩阵变宽了 |
| Attention FLOPs | 是（序列长度相关） | 但小 batch 下计算不是瓶颈 |
| All-reduce 通信 | 否 | 通信量由模型分片决定 |

所以“GPU 运算压力”确实变大了，但运算单元没饱和，真正卡住的是内存带宽和通信。只要增加的这些 FLOPs 没有突破计算单元的吞吐上限，walltime 就不会明显增加。

## Course Update Recommendation

建议在 m0-problem 中加入一个“FLOPs 增加 ≠ 延迟增加”的小节，用 memory-bound / compute-bound 的区分来解释。这是读者最容易混淆的点。
