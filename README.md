# CloudSimPy 数据中心作业调度仿真框架 - 修改版本

## 拟增加feature:

- [x] 增加更多log
    - [x] log层级: info / debug
    - [ ] log参数注入
- [ ] 集成[Gandiva](https://we5lw6jk7r.feishu.cn/wiki/wikcnLjzQuk89nrhUDQZy56qjzh)
- [ ] 集成[Tiresias](https://we5lw6jk7r.feishu.cn/wiki/wikcnzr0Uw239jWOtVFdX1In00b)
- [ ] 优化强化学习
    - [x] 支持Tensorflow-gpu
    - [ ] 支持Tensorflow 2.0
    - [ ] 支持Pytorch
- [ ] 集成...

## 目前亟待解决的问题

- [ ] 目前使用的方式应该不是一个合理使用强化学习的方式
    - [ ] 没有合理使用mini-batch，而是用一堆for-loop，看起来效率不高