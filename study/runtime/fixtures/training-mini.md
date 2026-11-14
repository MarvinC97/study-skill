# 训练过程示例

## Next Token Prediction

Next Token Prediction 让模型根据上下文预测下一 token。Loss 衡量目标 token 与预测分布的偏差。训练参数更新会改变类似上下文的概率分布。单次概率改善不等于稳定能力。

## SFT 与 RL

SFT 从示范目标 token 学习回答格式。RL 通过任务奖励调整策略。奖励错误会鼓励错误行为，评估环境必须与训练环境适度隔离。
