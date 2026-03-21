# Space One 拼房实验室 - 项目进展记录

## 项目概述
微信小程序：会议活动室友匹配系统

## Claude 对话管理

### 当前对话 Session ID
```
aadbbf29-4f91-447e-85eb-a917352a81dd
```

### 恢复对话命令
```bash
claude --resume aadbbf29-4f91-447e-85eb-a917352a81dd
```

### 查看所有对话列表
```bash
claude --list
```
会显示所有对话的 ID、时间和摘要

### 在项目目录启动（自动恢复）
```bash
cd "/Users/songsongsong/Library/Mobile Documents/com~apple~CloudDocs/同步盘/INNOVATION MAP/赵嵩项目/202601编程思维课/Roomie-Claude"
claude
```
如果之前在这个目录有对话，会自动恢复

## 最新状态（2026-02-21）

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

#### 8. FAQ 页面（2026-02-21 新增）
- ✅ FAQ 页面开发（8 个常见问题）
- ✅ 全展开设计，所有内容一次性显示
- ✅ 首页添加 FAQ 入口
- ✅ 紫色渐变背景，白色卡片设计

#### 9. 开发环境
- ✅ SSH密钥免密登录（本地→服务器）
- ✅ 服务器API部署（49.233.127.228:5000）
- ✅ 数据持久化（room_data.json）
- ✅ 文件锁机制（fcntl）防止并发写入冲突

### 技术架构

#### 前端（微信小程序）
- 原生开发（WXML + WXSS + JS）
- 页面：index（首页）、create（创建活动）、form（填表）、result（结果）、agreement（协议）、wish（许愿）、faq（常见问题）
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

### 2026-02-21 更新内容

#### 新增功能
1. **FAQ 页面**
   - 创建完整的 FAQ 页面（faq.wxml, faq.wxss, faq.js, faq.json）
   - 包含 8 个常见问题（功能介绍、匹配规则、安全性、活动口令等）
   - 全展开设计，所有内容一次性显示，无需点击
   - 紫色渐变背景，白色卡片设计
   - 首页添加 FAQ 入口："❓ 我能用这个小程序做什么"

2. **批量测试脚本**
   - 创建 `test_pending_mechanism.py` 批量测试脚本
   - 测试 6 个场景：pending 创建、确认匹配、拒绝匹配、history 防重复、批量匹配、并发确认
   - 自动化测试 pending 机制的完整流程

3. **真机测试准备**
   - 创建《真机测试用户清单.md》，包含 10 个测试用户
   - 创建配套测试脚本：`create_real_test_users.py`、`check_test_status.py`、`clean_test_data.py`
   - 完成真机测试，验证所有核心功能

4. **开发工作流优化**
   - 在 `2026-02-01-programming-notes.md` 中添加终端快捷键文档
   - 记录删除操作、光标移动、历史命令等快捷键
   - 建立"复杂命令写成文件"的工作流规范

#### 优化改进
1. **统计接口优化**
   - 修改 `api.py` 的 `/api/check_code` 接口
   - 增加 `pending_count` 统计
   - 从 2 个状态统计（active, matched）改为 3 个（active, pending, matched）

2. **创建活动页面优化**
   - 修改 `create.wxml` 的 placeholder 示例
   - 活动名称改为中文示例："人工智能峰会"
   - 城市改为中英文都可："北京 或 Beijing"
   - 自定义后缀注释改为："用于区分同一活动的不同群组"

#### 修改的文件
- `api.py`
  - 修改 /api/check_code 接口，增加 pending_count 统计

- `miniprogram/pages/faq/` (新增)
  - `faq.wxml` - FAQ 页面结构
  - `faq.wxss` - FAQ 页面样式
  - `faq.js` - FAQ 页面逻辑（8 个问题）
  - `faq.json` - FAQ 页面配置

- `miniprogram/pages/index/`
  - `index.wxml` - 添加 FAQ 入口链接
  - `index.wxss` - 添加 FAQ 链接样式
  - `index.js` - 添加 goToFaq 导航函数

- `miniprogram/app.json`
  - 注册 FAQ 页面

- `miniprogram/pages/create/create.wxml`
  - 优化 placeholder 和 hint 文案

- `2026-02-01-programming-notes.md`
  - 添加终端快捷键文档
  - 添加命令执行最佳实践

- 测试脚本（新增）
  - `test_pending_mechanism.py` - 批量测试脚本
  - `create_real_test_users.py` - 创建测试用户
  - `check_test_status.py` - 检查用户状态
  - `clean_test_data.py` - 清理测试数据
  - `真机测试用户清单.md` - 测试用户列表

### 2026-02-23 更新内容

#### 小程序上传优化
1. **代码上传到微信后台**
   - 首次上传小程序代码到微信公众平台
   - 版本号：1.0.0
   - 状态：开发版本已上传，等待备案通过后提交审核

2. **包体积优化**
   - 压缩 logo.png (1523KB) → logo.jpg (108KB)，压缩率 92.9%
   - 删除旧的 PNG 文件，更新所有引用路径
   - 主包大小从超过 1.5MB 优化到 296KB
   - 图片尺寸保持 1024x1024，仅降低 JPEG 质量到 85

3. **启用组件按需注入**
   - 在 app.json 中添加 `"lazyCodeLoading": "requiredComponents"`
   - 减少小程序启动时的代码加载量

4. **创建工具脚本**
   - `compress_images.py` - 图片压缩脚本（支持自动调整质量和尺寸）
   - `sync_to_server.sh` - 服务器同步脚本

#### 修改的文件
- `miniprogram/app.json`
  - 添加 lazyCodeLoading 配置

- `miniprogram/images/`
  - 新增 logo.jpg (108KB)
  - 删除 logo.png (1523KB)

- `miniprogram/pages/index/index.wxml`
  - 更新背景图引用：logo.png → logo.jpg

- `miniprogram/pages/result/result.wxml`
  - 更新背景图引用：logo.png → logo.jpg

- 工具脚本（新增）
  - `compress_images.py` - 图片压缩工具
  - `sync_to_server.sh` - 服务器同步工具

### 下一步计划

#### 待操作清单

1. **小程序发布**
   - [x] 代码上传到微信后台（已完成）
   - [x] 包体积优化（已完成）
   - [ ] 等待备案通过
   - [ ] 提交微信审核

2. **上线准备**
   - [ ] 小程序备案（进行中）
   - [ ] 配置服务器域名白名单
   - [ ] 启用 OpenID（正式上线后）
   - [ ] 清理测试数据

3. **可选优化**
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
- 状态：备案中，代码已上传（v1.0.0）

### 测试数据
- 群口令：ASBJ0328
- 测试通过：pending 机制、倒计时、自动取消
- 真机测试：已验证 onHide 自动拒绝功能
- 包体积：296KB（优化后）

---

**最后更新**: 2026-02-23
**状态**: 代码已上传微信后台，包体积优化完成，等待备案通过后提交审核

---

### 2026-03-01 网页版上线
- 网页版完整拼房流程上线
- 小程序首次提交审核

---

### 2026-03-04 第二轮改版（应对第一次审核被拒）

**被拒原因**：wechat_id 字段明确收集微信号，违反规则 3.4

**改动内容**：
- `form.wxml/js/wxss`：wechat_id 改为单行自由填写，标签"如何联系你"，无提示语，移至表单底部，去掉英文限制，白色背景，修复溢出问题
- `result.wxml/js/wxss`：确认匹配后才显示对方留言（showMessage 机制），确认后只剩全宽"返回首页"，删除"许个愿"入口
- `wish.wxml/js`：删除联系方式字段
- `agreement.wxml`：所有"微信号"改为"您留下的联系方式"，删除"微信 OpenID"条目
- `app.json`：添加 `usePrivacyCheck: true`
- `app.js`：启用 `doLogin()`，添加 `wx.onNeedPrivacyAuthorization` 隐私弹窗
- `form.wxss`：容器加 `overflow-x: hidden` 防左右晃动，input 加白色背景

---

### 2026-03-05 第三轮改版（应对第二次审核被拒）

**被拒原因1**：`/api/login` 响应中明文传输 session_key
- `api.py`：删除响应里的 `session_key` 字段，只返回 `openid`

**被拒原因2**：许愿页属于用户反馈功能，个人主体不允许
- `app.json`：删除 `pages/wish/wish` 页面注册
- `index.wxml`：删除"我有想法"入口
- `index.js`：删除 `goToWish()` 方法

**最后更新**: 2026-03-08
**状态**: 小程序搁置，重心转向网页版

---

### 2026-03-16 创新地图活动招募文案

**本次工作内容**：为创新地图两个即将举办的活动制作招募文案和客服回复库。

**深圳游学2026（4月10-11日）**
- 主题：中国供应链与中国制造
- 新建文件夹 `深圳游学2026/`，包含：
  - `客服回复库.md`：完整FAQ，含定价逻辑、退款政策、住宿安排
  - `公众号招募文案.md`：强调深圳是窗口，中国制造是主题
  - `朋友圈短文.md`：200字群发版本
- 定价：正价5,980元；历届科技营85折5,083元；当期会员二选一（85折或带人各2,990元）；住宿±700元

**硅谷游学2026（5月10-16日）**
- 主题：AI全产业链（硬件→大模型→云→应用→龙虾聚会）
- 新建文件夹 `硅谷游学2026/`，包含：
  - `公众号招募文案.md`：以OpenClaw龙虾热潮和AI编程爆发开篇，全产业链展开，龙虾聚会压轴
- 定价：正价108,000元；科技特训营早鸟价86,000元（4月10日前）
- 确认参访：谷歌（大模型）、英伟达、Meta、斯坦福StartX、纳斯达克创业中心

**最后更新**：2026-03-16
**状态**：深圳游学文案完成；硅谷游学文案完成初版

---

### 2026-03-22 飞书机器人上线 + 航海家大会数据监控

#### 背景
航海家大��（HHHZ0327，杭州，3月27-30日，预计1500人）正式开始招募，网页版拼房系���实际投入使用。

#### 完成内容

1. **服务器 SSH 密钥配置**
   - 本地生成 ed25519 密钥，公钥添加至服务器 authorized_keys
   - Claude 可直接访问服务器查看数据

2. **飞书机器人推送（新增 `roomie_notify.py`）**
   - 监控 room_data.json 变化
   - 有新用户加入 → 推送通知（含姓名、当前总人数��
   - 有新匹配成功 → 推送通知（含双方姓名、日期、习惯）
   - 服务器 crontab 每 15 分钟运行一次
   - 快照文件：`notify_snapshot.json`（记录上次状态，防重复推送）

3. **数据观察（截至 2026-03-22）**
   - 航海家大会：62 人进入，18 对匹配成功，26 人等待
   - 等待原因：男多女少、日期错开、吸烟习惯不兼容、噪音要求不匹配

#### 新增文件
- `roomie_notify.py` — 飞书推送脚本（本地 + 服务器均有）
- 服务器 `notify_snapshot.json` — 自动生成，无需手动维护

**最后更新**：2026-03-22
**状态**：飞书机器人运行中，每 15 分钟推送一次

---



- 域名备案通过：myspaceone.com
- 安装 nginx，配置反向代理（80端口 → Flask 5000端口）
- 腾讯云安全组开放 80、443 端口
- Let's Encrypt 申请 SSL 证书，HTTPS 正常
- 网页版 API 地址从 IP 改为 https://myspaceone.com
- 正式访问地址：**https://myspaceone.com**

**最后更新**: 2026-03-11
**状态**: 网站正式上线，域名+HTTPS 配置完成

---

### 2026-03-08 小程序搁置

**第三次审核被拒原因**：口令生成页被认定为社交平台功能，个人主体不允许经营

**决定**：小程序暂时搁置，优先推进网页版。待网站备案通过、业务跑通后，视情况注册企业主体再重新提审。

**当前小程序状态**：
- 代码完整，功能正常，随时可重新提审
- 若重新提审，建议删除口令生成页（create 页），改为后台手动创建口令
- openid 已启用，session_key 泄露问题已修复

**下一步重心**：网页版 + 域名备案
