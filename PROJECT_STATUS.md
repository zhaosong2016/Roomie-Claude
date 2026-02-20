# Space One 拼房实验室 - 项目进展记录

## 项目概述
微信小程序：会议活动室友匹配系统

## 最新状态（2026-02-20）

### 已完成功能

#### 1. 核心匹配功能
- ✅ 用户信息提交（姓名、微信号、性别、日期、吸烟、作息、噪音习惯）
- ✅ 智能匹配算法（完全匹配：性别、日期、吸烟、噪音兼容性）
- ✅ 噪音锁定规则（弱鸡vs低音炮互斥）
- ✅ 匹配成功显示完整信息（包括对方习惯）
- ✅ **Pending 确认机制**（匹配后需用户确认，防止误匹配）

#### 2. Pending 状态管理（2026-02-20 新增）
- ✅ 匹配成功后进入 pending 状态，不自动确认
- ✅ 60 秒倒计时，用户需在倒计时内选择
- ✅ 用户可选择"复制微信号"（确认匹配）或"重新匹配"（拒绝匹配）
- ✅ 倒计时结束自动拒绝匹配，返回首页
- ✅ 用户关闭小程序自动拒绝匹配（onHide 机制）
- ✅ 后端 60 秒超时自动清理（兜底机制）
- ✅ 拒绝匹配后双方加入 history，不会再次匹配
- ✅ Pending 状态用户重新提交时显示匹配信息和倒计时

#### 3. 部分匹配推荐（第二次提交）
- ✅ 用户第二次提交时，如果没有完全匹配
- ✅ 显示"除了日期外都匹配"的潜在室友
- ✅ 计算并显示日期重叠区间
- ✅ 建议用户调整日期重新匹配

#### 4. 重新匹配功能
- ✅ 已匹配用户重复提交 → 显示"你已匹配过XXX"
- ✅ 显示完整匹配信息（委婉表述：睡眠声响、噪音容忍度等）
- ✅ "去加微信"按钮 → 复制微信号到剪贴板
- ✅ "重新匹配"按钮 → 确认弹窗 → 解除双方匹配 → 10秒后返回首页
- ✅ 后端/api/unmatch接口

#### 5. 用户体验优化
- ✅ 用户协议弹窗（左对齐显示，可点击查看）
- ✅ 输入框自动触发英文键盘（口令、微信号）
- ✅ 微信号输入实时过滤（只允许英文、数字、下划线、横杠）
- ✅ 日期选择器禁止选择过去日期
- ✅ 结果页文字优化（"快联系TA吧"）
- ✅ 背景图片设计（首页、结果页）
- ✅ 统一按钮样式（#007aff蓝色）
- ✅ 导航栏白色背景
- ✅ 倒计时提示样式（黄色警告框）

#### 6. 微信登录集成
- ✅ 后端/api/login接口（code换openid）
- ✅ 前端app.js自动登录（已禁用，开发阶段用wechat_id）
- ✅ OpenID防刷单机制（可选，兼容旧数据）
- ✅ 配置：AppID和AppSecret已设置

#### 7. 群组管理
- ✅ 创建活动接口（生成群口令）
- ✅ 口令规则：会议名+城市+日期+自定义后缀
- ✅ 口令验证（显示等待/已匹配人数）

#### 8. 开发环境
- ✅ SSH密钥免密登录（本地→服务器）
- ✅ 服务器API部署（49.233.127.228:5000）
- ✅ 数据持久化（room_data.json）
- ✅ 文件锁机制（fcntl）防止并发写入冲突

### 技术架构

#### 前端（微信小程序）
- 原生开发（WXML + WXSS + JS）
- 页面：index（首页）、create（创建活动）、form（填表）、result（结果）
- AppID: wxff98b80705277ab6

#### 后端（Flask API）
- Python 3 + Flask + Flask-CORS
- 部署：腾讯云服务器 49.233.127.228:5000
- 数据存储：JSON文件（room_data.json）
- 依赖：requests, pypinyin

#### API接口
- POST /api/create_activity - 创建活动生成口令
- POST /api/login - 微信登录（code换openid）
- POST /api/submit - 提交用户信息并匹配
- POST /api/confirm - 确认匹配（pending → matched）
- POST /api/reject - 拒绝匹配（pending → active，加入history）
- POST /api/unmatch - 解除匹配（matched → active，加入history）
- GET /api/check_code - 验证群口令
- GET /api/stats - 获取统计数据
- GET /api/check_match - 检查匹配状态
- GET /api/health - 健康检查

### 当前问题

#### 已解决
- ✅ OpenID在开发阶段导致用户覆盖 → 已禁用OpenID，用wechat_id区分
- ✅ API文件损坏（sed操作错误）→ 已修复
- ✅ user1/user2数据不完整 → API已修复，重新创建完整版本
- ✅ 微信号输入允许中文 → 已添加实时过滤，只允许英文数字
- ✅ 匹配后自动确认 → 已改为 pending 状态，需用户确认
- ✅ 倒计时不显示 → 已修复，后端返回 is_pending 标志
- ✅ 关闭小程序不取消匹配 → 已修复，使用 onHide 机制
- ✅ clean_expired_pending 只检查第一个用户 → 已修复，删除错误的 return 语句
- ✅ Pending 用户重新提交显示"等待匹配" → 已修复，检查 pending 状态

#### 已知设计选择（非 bug）
- 单方确认即算匹配成功（避免双方等待僵局，不满意可解除）
- 60 秒超时作为兜底机制（onHide 可能失败时的保障）

### 2026-02-20 更新内容

#### 新增功能
1. **Pending 确认机制**
   - 匹配成功后不自动确认，进入 pending 状态
   - 60 秒倒计时，用户需主动选择
   - 支持确认（复制微信号）或拒绝（重新匹配）
   - 倒计时结束自动拒绝

2. **自动取消机制**
   - 用户关闭小程序时自动拒绝匹配（onHide）
   - 后端 60 秒超时自动清理（兜底）
   - 拒绝后双方加入 history，不会再次匹配

3. **状态流转**
   - active → pending（匹配成功）
   - pending → matched（用户确认）
   - pending → active（用户拒绝/超时/关闭）
   - matched → active（解除匹配）

#### 修复的 Bug
1. 微信号输入允许中文 → 添加实时过滤
2. 倒计时不显示 → 后端返回 is_pending 标志
3. 关闭小程序不取消匹配 → 使用 onHide 代替 onUnload
4. clean_expired_pending 只检查第一个用户 → 删除错误的 return
5. Pending 用户重新提交显示"等待匹配" → 检查 pending 状态

#### 修改的文件
- `api_final.py`
  - 添加 clean_expired_pending 函数
  - 添加 /api/confirm 和 /api/reject 接口
  - 修改 /api/submit 返回 is_pending 标志
  - 修复 clean_expired_pending 的 return 错误
  - 修改匹配逻辑，检查 pending 状态

- `result.js`
  - 添加 countdown 和 isPending 状态
  - 添加 startCountdown 倒计时函数
  - 添加 onHide 自动拒绝机制
  - 修改 onCopyWechat 调用 /api/confirm
  - 修改 doReject 调用 /api/reject

- `result.wxml`
  - 添加倒计时提示显示

- `result.wxss`
  - 添加 countdown-tip 样式

- `form.js`
  - 添加 onWechatInput 过滤非法字符
  - 修复 group_code 保存到 globalData

### 下一步计划

#### 待操作清单

1. **代码部署**
   - [ ] 将本地 api_final.py 部署到服务器
   - [ ] 重启服务器 API 服务
   - [ ] 验证 API 正常运行

2. **小程序发布**
   - [ ] 重新编译小程序
   - [ ] 真机测试 pending 功能
   - [ ] 提交微信审核（需要备案完成）

3. **上线准备**
   - [ ] 小程序备案（进行中）
   - [ ] 配置服务器域名白名单
   - [ ] 启用 OpenID（正式上线后）
   - [ ] 清理测试数据

4. **可选优化**
   - [ ] 添加用户反馈收集
   - [ ] 添加数据导出功能
   - [ ] 优化倒计时时长（根据用户反馈调整）

#### 暂不实施
- 新闻推送脚本（延后）
- 双方确认机制（当前单方确认已足够）

### 文件说明

#### 重要文件
- `api_final.py` - 最新完整API代码（本地）
- 服务器：`/root/Roomie-Claude/api.py` - 运行中的API
- 服务器：`/root/Roomie-Claude/room_data.json` - 数据文件

#### 小程序目录
- `Roomie-Claude/miniprogram/` - 小程序源码
- `Roomie-Claude/miniprogram/pages/` - 页面文件
- `Roomie-Claude/miniprogram/app.js` - 全局配置（OpenID已禁用）

#### 备份文件
- `api_submit_fixed.py` - 正确的submit函数
- `api_backup_broken.py` - 损坏的备份
- `api_clean.py` - 清理版本

### 服务器信息
- IP: 49.233.127.228
- SSH: root@49.233.127.228（已配置密钥登录）
- API端口: 5000
- 工作目录: /root/Roomie-Claude/
- 日志: /root/Roomie-Claude/api.log

### 微信小程序配置
- AppID: wxff98b80705277ab6
- AppSecret: f251b2106c7655ab8b5bc7cfd5d5190e
- 状态：备案中

### 测试数据
- 群口令：ASBJ0328
- 测试通过：pending 机制、倒计时、自动取消
- 真机测试：已验证 onHide 自动拒绝功能

---

**最后更新**: 2026-02-20
**状态**: Pending 机制开发完成并测试通过，待部署上线
