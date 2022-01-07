# CloudSimPy 数据中心作业调度仿真框架 - 修改版本

## 拟增加feature:

- [x] 增加更多log
    - [x] log层级: info / debug
    - [ ] log参数注入
- [ ] 改造成深度学习环境
    - [x] 增加GPU
    - [x] 增加GPU-memory
    - [ ] 接入一个开源数据集
    - [ ] 对Instance进行ps-worker改造
    - [ ] 同一个task中Instance的执行时间不同
- [ ] 改造集群环境
    - [x] **静态方法**: 支持集群在特定时刻进行扩展GPU/机器数量
    - [ ] **动态方法**: 支持集群在特定时刻进行扩展GPU/机器数量
    - [ ] 支持一个Instance可以在多台机器上执行 ⚠存疑: 这里是否需要这种设计
    - [ ] 接入网络延迟
- [ ] 集成[Gandiva](https://we5lw6jk7r.feishu.cn/wiki/wikcnLjzQuk89nrhUDQZy56qjzh)
- [x] 集成[Tiresias](https://we5lw6jk7r.feishu.cn/wiki/wikcnzr0Uw239jWOtVFdX1In00b)
    - [x] 支持执行过程中暂停instance的进行
    - [x] 支持instance粒度的调度算法
- [ ] 优化强化学习
    - [ ] 接入一个新的强化学习算法
    - [x] 支持Tensorflow-gpu
    - [ ] 支持Tensorflow 2.0
    - [ ] 支持Pytorch


## 目前亟待解决的问题

- [ ] 目前使用的方式应该不是一个合理使用强化学习的方式
    - [ ] 没有合理使用mini-batch，而是用一堆for-loop，看起来效率不高