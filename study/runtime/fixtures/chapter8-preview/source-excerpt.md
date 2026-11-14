# Chapter 8 source excerpt · preview pages P001–P002 only

**Source**: https://github.com/bojieli/ai-agent-book/blob/main/book/chapter8.md
**Git blob SHA**: 38eb64bf45b9e844b6bdbcbedfc61b9dcc12244b
**Scope**: chapter opening, “从预训练到 RL：四阶段全景” and “预训练在做什么：预测下一个词”.
This is an intentionally partial source excerpt for validating two pages; do not use it to claim complete Chapter 8 coverage.

## Four phases (selected source wording)

“先建立一张最重要的地图：现代模型的能力开发通常可以拆成四个环节。”

- 预训练（Pre-training）：在海量互联网文本上做“预测下一个词”的训练；建立通用语言规律、世界知识和基本推理能力。
- Mid-training：从已有基础模型出发，在目标语言、领域文档、代码、长上下文或经过设计的能力数据上继续做语言建模，补齐知识与基础能力。
- SFT（Supervised Fine-Tuning）：用输入—理想输出示范数据，让模型学习输出格式、风格、流程及指令遵循。
- RL（Reinforcement Learning）：模型自己生成行为，通过任务环境与奖励反馈提高高奖励行为的概率。

Source conditions: 两条主线强调（a）在本章有限示范与分布变化的对照实验中，SFT 更易过拟合，而 RL 迁移表现更好；这不是普遍结论，（b）数据和环境是后训练的重要条件。四阶段是常见路径，项目可以跳过不需要的阶段。

## Next Token Prediction (selected source wording)

“现代大模型的全部‘智能’，都建立在一个简单到令人意外的任务上：预测下一个词（Next Token Prediction，NTP）。”

给模型看一段文本的前半部分，让它猜下一个 token。输入“中国的首都是”，模型应给“北京”较高概率。预测与真实 token 的差距形成 Loss，训练更新参数，让目标 token 在相似上下文下更容易被预测。

“模型的输出本质上是一个概率分布”。模型为候选 token 分配概率。Mid-training 继续类似 NTP；SFT 使用输入—输出示范并通常只计算回答 token 的 Loss。目标 token 的局部概率提升不自动证明模型具有稳定可迁移能力。
