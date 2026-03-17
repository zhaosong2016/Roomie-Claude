# Roomie-Claude 项目记忆

## 项目基本信息
- 名称：Space One 拼房实验室（小程序 + 网页版）
- 后端服务器：`http://49.233.127.228:5000`，数据文件 `/root/Roomie-Claude/room_data.json`
- 小程序目录：`miniprogram/`，后端：`api.py`
- 网页版已上线，小程序审核中

## 当前状态（2026-03-05）
- 网页版正常运行
- 小程序第二次审核被拒，已完成第三轮改版，准备再次提交审核

## 审核被拒及修复（2026-03 第二轮）
**拒绝原因1**：`/api/login` 响应中明文传输 session_key（安全问题）
- 修复：`api.py` 删除响应里的 `session_key` 字段，只返回 `openid`

**拒绝原因2**：许愿页属于用户反馈功能，个人主体不允许
- 修复：删除 `pages/wish/wish` 页面注册（app.json）
- 删除 index.wxml 的"我有想法"入口
- 删除 index.js 的 `goToWish()` 方法

## 审核被拒及修复（2026-03 第一轮）
**拒绝原因**：wechat_id 字段明确收集微信号，违反规则 3.4

**修复内容**：
1. `form.wxml/js/wxss`：wechat_id 改为单行 input，标签"如何联系你"，无提示语，挪到表单最底部，去掉英文限制，白色背景，去掉 `width:100%`（防溢出）
2. `result.wxml/js/wxss`：确认匹配后才显示对方留言（showMessage 机制），确认后只剩全宽"返回首页"，删除"重新匹配"和"许个愿"
3. `wish.wxml/js`：删除联系方式字段
4. `agreement.wxml`：所有"微信号"改为"您留下的联系方式"，删除"微信 OpenID"条目
5. `app.json`：添加 `"usePrivacyCheck": true`
6. `app.js`：启用 `doLogin()`，添加 `wx.onNeedPrivacyAuthorization` 隐私弹窗
7. `form.wxss`：容器加 `box-sizing: border-box` + `overflow-x: hidden` 防左右晃动

## 关键技术细节

### form.wxss 注意事项
- `.input` 不能加 `width: 100%`（会导致加上 padding/border 后溢出屏幕）
- `.input` 不能加 `box-sizing: border-box`（会导致 native input 渲染异常变小）
- 正确做法：不设 width，让 block 元素自然撑满，加 `background: #fff`
- `.container` 加 `box-sizing: border-box; overflow-x: hidden` 防晃动

### 匹配逻辑
- 第一次提交（submit_count < 2）：严格匹配所有条件
- 第二次及以后（submit_count >= 2）：部分匹配，且跳过 submit_count < 2 的用户
- **同一设备（同一 openid）提交的两个用户不会互相匹配**（自我识别机制）
- 测试匹配需要两个不同微信账号，或临时将 openid 设为空字符串

### 服务器常用命令（单行，从聊天记录复制）
查看某群组数据：
```bash
python3 -c "import json; data=json.load(open('room_data.json')); users=[u for u in data['users'] if u.get('group_code')=='HZHZ0328']; [print(u.get('name'),'|',u.get('wechat_id'),'|',u.get('status'),'|',u.get('check_in'),'-',u.get('check_out')) for u in users]"
```
清空某群组数据：
```bash
python3 -c "import json;d=json.load(open('room_data.json'));d['users']=[u for u in d['users'] if u.get('group_code')!='HZHZ0328'];json.dump(d,open('room_data.json','w'),ensure_ascii=False,indent=2)"
```
清空所有数据并格式化：
```bash
python3 -c "import json;d=json.load(open('room_data.json'));d['users']=[];d['stats']={'total_users':0,'total_matches':0};json.dump(d,open('room_data.json','w'),ensure_ascii=False,indent=2)"
```
- **注意：始终从聊天记录复制命令，不要从终端输出复制（会串行）**

## 用户偏好
- 服务器端命令需要单行，不能有换行/缩进
- 沟通直接，不需要过多解释
