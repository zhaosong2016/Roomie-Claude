# Day 1 
- 学习了安装python3（复习）
- 学用python读取cvs文件（读了一个血氧表）

# Day 2 

调用 API
- 学习了花括号和方括号在编程代码里的区别
- 区分了什么是数据，什么是指令
- 建了一个 GitHub 上的账号，用来学习怎么不断在同一个文件里更新一个笔记，还能每天留痕 用户名是zhaosong2016 是用谷歌账号登录的
建账号的时候，代理服务器总是出问题。然后学了一个在终端上退出代理服务器的操作。以下是操作：
解决方案：清除 Git 的代理配置
步骤 1：打开终端（Terminal）
• 按 Cmd + 空格，输入 Terminal，回车
步骤 2：检查 Git 当前是否设置了代理
git config --global http.proxy
git config --global https.proxy
如果返回类似 http://127.0.0.1:7890，说明 Git 还在用代理。
步骤 3：清除 Git 代理设置
# 清除 HTTP 代理
git config --global --unset http.proxy
# 清除 HTTPS 代理  
git config --global --unset https.proxy
💡 如果提示 “not found”，说明没有设置，可以跳过。
步骤 4：验证是否清除成功
git config --global http.proxy
git config --global https.proxy
应该没有任何输出（空行）。

练习搭子从千问转到了gemini，教我下载了VS code，现在用VS Code写代码了
正在熟悉VS Code的界面，我的笔记没有存在编程思维课的文件夹里，而是存在桌面上的gh-try文件夹了，试了从苹果总菜单那里的“文件”——“将文件夹”添加到工作区“把笔记文件所在的文件夹也放到工作区了，学会了

--- 查询成功！---
用户名: zhaosong2016
ID编号: 258533809
账号创建时间: 2026-02-01T02:55:12Z
目前的粉丝数: 0

# 📅 Day 2 执行卡片

## ✅ 3个核心收获
1.  学会了安装第三方库：`pip install requests` 是给 Python 装抓取数据的装备。
2.  理解了 JSON：它是Python 能直接读懂的“纯数据字典”。
3.  成功调用 API：用 `requests.get()` 给 GitHub 打电话，并查到了自己的注册时间。
--- 查询成功！---
用户名: zhaosong2016
ID编号: 258533809
账号创建时间: 2026-02-01T02:55:12Z
目前的粉丝数: 0

## ❓ 1个疑问
在VS code里面，它自动把代码标成不同颜色，分别是什么意思？
弄明白了，就是给不同性质的代码标上不同的颜色，方便快速识别它到底是什么，以此来辅助排查 bug。

## 💡 1个感悟
以前看程序员的代码，尤其是彩色的代码，总会有种崩溃的感觉。
今天突然觉得这些彩色的代码，大致意思能懂一点点了。而且当这些颜色有了意义以后，看着就不那么恐怖了。

另外，我的原计划是每天花一个小时学习。但是今天周日在家里把前两讲学完，差不多用了四五个小时。

感觉进度太慢了，效率有点低。可能是因为前面的基础太薄弱，希望以后能加速。

还有一个领悟：我们用鼠标点点点的图形界面，实际上只是为了让不会编程的人能更直观、友好地使用电脑。
但有时候等了半天也实现不了的工作，你只要用终端的指令，一下就能完成。所以，还是程序员拥有最高的权限呀

  🚀 服务器操作完整笔记
                                                                                                        
  第一部分：进入与离开（大门钥匙）                                                                      
                                                                                                        
  登录服务器                                                                                            
                                                                                                        
  ssh root@49.233.127.228

  目录导航

  cd /root/Roomie-Claude    # 进入项目文件夹
  cd ~                       # 回到"家"目录
  cd /                       # 回到系统根目录
  cd ..                      # 往回退一级
  exit                       # 离开服务器

  ---
  第二部分：查看与管理（巡视领地）

  查看文件和目录

  ls                         # 看当前目录下有哪些文件
  ls -la                     # 看详细信息（包括隐藏文件）
  cat api.py                 # 看文件内容（不修改）
  cat room_data.json         # 看实时数据
  tail -50 api.log           # 看日志最后50行
  tail -f api.log            # 实时查看日志（Ctrl+C停止查看）

  搜索和查找

  grep -n "check_code" api.py           # 在文件中搜索关键词
  wc -l api.py                          # 统计文件行数

  ---
  第三部分：文件编辑（手术刀）

  方法1：Vim编辑（推荐）

  完全替换文件内容：
  vim api.py
  进入vim后：
  1. 按 gg - 跳到文件开头
  2. 按 dG - 删除所有内容
  3. 按 i - 进入插入模式
  4. Cmd+V - 粘贴新内容
  5. 按 Esc - 退出插入模式
  6. 输入 :wq 然后回车 - 保存并退出

  Vim常用命令：
  - i - 进入插入模式
  - Esc - 退出插入模式
  - :wq - 保存并退出
  - :q! - 不保存强制退出
  - gg - 跳到文件开头
  - G - 跳到文件末尾
  - dG - 删除从当前位置到文件末尾

  方法2：Nano编辑

  nano api.py                # 普通修改
  true > api.py && nano api.py    # 清空后编辑
  退出三步走：Ctrl+O → 回车 → Ctrl+X

  ---
  第四部分：数据管理

  清空数据文件

  # 清空用户数据
  echo '{"users": [], "stats": {"total_matches": 0}}' > room_data.json

  # 验证清空成功
  cat room_data.json

  ---
  第五部分：运行与排错（点火起飞）

  前台运行（用于调试）

  python3 api.py
  特点：
  - 显示实时日志
  - 终端被占用
  - 按 Ctrl+C 停止
  - 关闭终端程序会停止

  后台运行（用于生产）

  nohup python3 api.py > api.log 2>&1 &
  特点：
  - 立即返回命令提示符
  - 日志保存到 api.log
  - 关闭终端程序继续运行
  - 不需要按 Ctrl+C

  解释：
  - nohup - 不挂断运行
  - > api.log - 把输出导流到文件（像个漏斗）
  - 2>&1 - 把错误信息也导流到同一个文件
  - & - 后台运行

  强制停止和重启

  # 方法1：杀掉占用端口的进程
  fuser -k 5000/tcp

  # 方法2：杀掉指定程序
  pkill -f "python3 api.py"

  # 方法3：强制杀掉
  pkill -9 -f "python3 api.py"

  # 重启服务完整流程
  pkill -f "python3 api.py"
  nohup python3 api.py > api.log 2>&1 &

  ---
  第六部分：前台 vs 后台运行

  判断程序状态

  有命令提示符 = 可以输入命令：
  [root@VM-0-12-opencloudos Roomie-Claude]#  ← 可以输入

  没有命令提示符 = 程序正在运行：
  Press CTRL+C to quit  ← 需要Ctrl+C停止

  什么时候按 Ctrl+C

  需要按：
  - 程序在前台运行
  - 想停止程序
  - 终端被占用，想输入新命令

  不需要按：
  - 程序在后台运行（命令末尾有 &）
  - 已经有命令提示符
  - 只是查看日志（tail -f）

  前台运行调试技巧

  开两个终端：

  终端1（运行程序）：
  python3 api.py
  # 保持运行，看实时日志

  终端2（测试）：
  curl "http://localhost:5000/api/health"

  从前台转到后台

  # 当前：python3 api.py 正在前台运行
  # 步骤1：按 Ctrl+C 停止
  # 步骤2：后台启动
  nohup python3 api.py > api.log 2>&1 &

  ---
  第七部分：测试接口

  测试API是否正常

  curl "http://localhost:5000/api/health"

  测试具体接口

  # 检查口令
  curl "http://localhost:5000/api/check_code?group_code=ASBE0328"

  # 创建活动
  curl -X POST http://localhost:5000/api/create_activity -H "Content-Type: application/json" -d
  '{"event_name":"AI Summit","city":"Beijing","date":"2026-03-28"}'

  ---
  第八部分：常见错误和解决

  错误1：Port 5000 is in use

  解决：
  fuser -k 5000/tcp
  nohup python3 api.py > api.log 2>&1 &

  错误2：curl: Failed to connect

  原因：API没有运行
  解决：
  # 检查
  curl "http://localhost:5000/api/health"
  # 启动
  nohup python3 api.py > api.log 2>&1 &

  错误3：vim粘贴后代码重复

  原因：没有先删除旧内容
  解决：gg → dG → i → 粘贴 → Esc → :wq

  错误4：404 Not Found

  原因：路由不存在或API没有正确加载
  解决：
  # 检查文件
  grep -n "@app.route" api.py
  # 重启API
  pkill -f "python3 api.py"
  nohup python3 api.py > api.log 2>&1 &

  ---
  第九部分：快捷键

  Mac终端快捷键

  - Cmd+左箭头 - 跳到行首
  - Cmd+右箭头 - 跳到行尾
  - Option+左箭头 - 按单词向左跳
  - Option+右箭头 - 按单词向右跳

  服务器快捷键

  - Ctrl+A - 跳到行首
  - Ctrl+E - 跳到行尾
  - Ctrl+C - 停止当前程序
  - Ctrl+D - 退出当前会话

  ---
  第十部分：完整操作流程

  修改代码并重启服务

  # 1. 停止旧进程
  pkill -f "python3 api.py"

  # 2. 编辑文件
  vim api.py
  # (gg → dG → i → 粘贴 → Esc → :wq)

  # 3. 后台启动
  nohup python3 api.py > api.log 2>&1 &

  # 4. 测试
  curl "http://localhost:5000/api/health"

  清空数据并重启

  # 1. 清空数据
  echo '{"users": [], "stats": {"total_matches": 0}}' > room_data.json

  # 2. 重启服务
  pkill -f "python3 api.py"
  nohup python3 api.py > api.log 2>&1 &

  ---
  记住这些，你就是服务器操作高手了！ 🎉

---
## 🚨 问题解决纪律（三次规则）

**核心原则：同一方法尝试3次未解决，立即换方案**

### 为什么需要这个规则
2026-02-17 在修复 `generate_group_code` 函数时，因为缩进和换行问题，用 sed/vim 远程修改反复失败超过10次，浪费了大量时间。最终用"本地创建文件+scp上传"的方法一次成功。

### 三次规则
1. **识别循环陷阱**
   - 同样的错误类型重复出现（如缩进错误、格式问题）
   - 修复一个问题又出现新问题
   - 超过5分钟还在处理同一个小问题

2. **立即切换方案**
   - 第1次失败：继续当前方法
   - 第2次失败：分析原因，调整方法
   - 第3次失败：**立即停止，换方案**

3. **优先级策略**
   - **代码文件**：优先用本地创建（Claude Write工具）+ scp上传
   - **简单修改**：可以用 sed/vim 远程编辑
   - **出现格式问题**：立即切换到本地创建

### 备选方案清单
| 场景 | 首选方案 | 备选方案1 | 备选方案2 |
|------|---------|----------|----------|
| 创建新文件 | 本地创建+scp | vim粘贴 | cat heredoc |
| 修改单行 | sed命令 | vim编辑 | 本地修改+scp |
| 替换整个文件 | 本地创建+scp | vim全删+粘贴 | - |
| 修改多行 | 本地创建+scp | vim编辑 | sed多次 |

### 实战案例
**问题**：修复Python函数缩进
- ❌ 失败方案：sed/vim远程修改（尝试10+次）
- ✅ 成功方案：Claude本地Write工具创建 → scp上传（1次成功）

**教训**：格式敏感的代码文件（Python、YAML等），直接用本地创建最可靠

 ## 📝 如何创建纯文本代码文件                  
                                                          
  ### 问题                                                
  Mac自带的"文本编辑"默认是**富文本模式**（RTF格式），保存
  的文件包含隐藏格式标记，Python无法识别，会报错：        
  SyntaxError: unexpected character after line            
  continuation character

  ### 解决方案：用VSCode创建（推荐）

  **步骤：**
  1. 打开VSCode
  2. 新建文件：`Cmd+N`
  3. 粘贴代码
  4. 保存：`Cmd+S`
  5. 输入文件名：`api_clean.py`
  6. 选择保存位置，点击"保存"

  **VSCode的优势：**
  - ✅ 自动识别纯文本格式
  - ✅ 代码高亮显示（容易发现错误）
  - ✅ 自动处理缩进
  - ✅ 不会有格式问题

  ### 备选方案：修改TextEdit设置

  如果必须用Mac自带的"文本编辑"：
  1. 打开"文本编辑"
  2. 菜单栏："文本编辑" → "偏好设置"
  3. 选择"**纯文本**"（不是"富文本"）
  4. 保存文件时，文件名输入 `.py` 扩展名

---

## 🔄 每日工作流程（2026-02-20 确定）

### 开工前准备
1. 阅读 `2026-02-01-programming-notes.md`（协作规范和技术知识）
2. 阅读 `PROJECT_STATUS.md`（项目进展和待办事项）

### 开发循环（一天多次）

```
本地修改代码（前端 + 后端）
  ↓
scp 上传到服务器（只上传 api.py）
  ↓
服务器重启服务（bash deploy.sh）
  ↓
测试小程序
  ↓
发现问题 → 继续修改（回到第一步）
```

**具体命令：**

```bash
# 1. 本地修改完成后，上传到服务器
cd "/Users/songsongsong/Library/Mobile Documents/com~apple~CloudDocs/同步盘/INNOVATION MAP/赵嵩项目/202601编程思维课/Roomie-Claude"
scp api.py root@49.233.127.228:/root/Roomie-Claude/

# 2. 在服务器上重启服务
# （登录服务器后执行）
cd /root/Roomie-Claude
bash deploy.sh
```

### 晚上收工（一天一次）

```bash
# 在本地 Roomie-Claude 目录
git add -A
git commit -m "📝 2026-02-XX: 今天的工作总结"
git push
```

### 重要说明

#### 代码 vs 数据
- **代码文件**（推 GitHub）：api.py、miniprogram/、*.md
- **数据文件**（不推 GitHub）：room_data.json、wishes.json、*.log

#### 为什么数据不推 GitHub？
1. 数据一直在变（每次有人提交都会变）
2. 数据只在服务器上有用（本地不需要）
3. 数据可能很大（影响 Git 性能）

#### 服务器上的 .gitignore 已配置
```
room_data.json
wishes.json
*.log
```

#### 只需本地推一次 GitHub
- 服务器上的数据文件一直留在服务器
- 定期用 `cp` 命令备份
- 不需要推 GitHub

### deploy.sh 脚本说明

**位置**：`/root/Roomie-Claude/deploy.sh`

**作用**：只负责重启服务，不负责更新代码

**内容**：
```bash
#!/bin/bash
echo "开始部署..."
cd /root/Roomie-Claude
pkill -f "python.*api.py"
sleep 2
nohup python3 api.py > api.log 2>&1 &
sleep 2
echo "部署完成！"
ps aux | grep api.py | grep -v grep
curl http://127.0.0.1:5000/api/health
```

### 常见问题

**Q: 为什么不在服务器上 git pull？**
A: GitHub 在国内访问不稳定，scp 上传更可靠。

**Q: 测试时用的是哪里的代码？**
A: 小程序（前端）在本地运行，但调用的是服务器上运行的 API（后端）。

**Q: 每次修改都要 scp 上传吗？**
A: 是的，后端代码必须在服务器上运行，小程序才能用。

**Q: 一天要推几次 GitHub？**
A: 只推一次，晚上所有工作完成后。避免一堆"修复bug"的提交。

---

## 💬 Claude 对话管理（2026-02-20）

### 什么是 Session ID？
每个 Claude 对话都有一个唯一的 ID（像身份证号），用来恢复之前的对话。

### 查看所有对话
```bash
claude --list
```
会显示：
- 所有对话的 Session ID
- 对话创建时间
- 对话摘要

### 恢复指定对话
```bash
claude --resume <session-id>
```

**示例：**
```bash
claude --resume aadbbf29-4f91-447e-85eb-a917352a81dd
```

### 在项目目录自动恢复
```bash
cd "项目目录路径"
claude
```
如果之前在这个目录有对话，会自动恢复最近的对话。

### 多个项目同时进行
可以同时开多个终端，每个终端运行不同的 Claude 对话：
```
终端1（Roomie-Claude）→ Claude A
终端2（新项目）      → Claude B
终端3（另一个项目）  → Claude C
```
它们互相独立，不会混淆。

### 退出和恢复
- 输入 `/exit` 退出对话
- 对话会自动保存
- 下次用 `--resume` 或在同目录启动即可恢复

### 最佳实践
1. **每个项目一个对话** - 避免混乱
2. **记录 Session ID** - 写在项目的 PROJECT_STATUS.md 里
3. **定期用 `--list` 查看** - 清理不需要的旧对话

---

## 🖥️ 服务器命令执行最佳实践（2026-02-21）

### 核心原则：复杂操作写文件，简单命令直接给

#### 方法1：写成文件（最推荐）✅

**适用场景：**
- 多行代码
- 复杂逻辑
- 需要重复使用
- Python 脚本、Shell 脚本

**流程：**
```
1. Claude 在本地写 .py 或 .sh 文件
   ↓
2. 用户用 scp 上传到服务器
   ↓
3. 服务器上执行
```

**示例：**
```bash
# 本地
scp clean_test_data.py root@49.233.127.228:/root/Roomie-Claude/

# 服务器
python3 clean_test_data.py
```

**优点：**
- ✅ 不会有粘贴换行问题
- ✅ 可以重复使用
- ✅ 代码清晰易读
- ✅ 可以加入 Git 版本控制
- ✅ 容易调试和修改

---

#### 方法2：简单命令直接给（次选）

**适用场景：**
- 单行命令
- 简短操作
- 不需要重复使用

**示例：**
```bash
ls -la
grep "xxx" file.txt
curl http://127.0.0.1:5000/api/health
python3 -c "print('hello')"
```

**优点：**
- ✅ 快速
- ✅ 不需要创建文件

---

#### 方法3：长命令用引号（避免使用）❌

**问题：**
- ❌ 粘贴时容易自动换行
- ❌ 引号嵌套容易出错
- ❌ 难以调试
- ❌ 缩进问题

**教训：**
2026-02-21 尝试用一行 Python 命令清理数据，粘贴时自动换行导致缩进错误，浪费时间。改用写文件方式一次成功。

---

### 决策树

```
需要在服务器执行命令？
  ↓
是否超过 1 行或包含复杂逻辑？
  ├─ 是 → 写成 .py 或 .sh 文件
  └─ 否 → 直接给命令
```

### 实战案例

**场景：清理测试数据**
- ❌ 失败方案：一行 Python 命令（粘贴换行错误）
- ✅ 成功方案：写成 clean_test_data.py 文件（一次成功）

---

## ⌨️ 终端快捷键（2026-02-21）

### 为什么终端不能 Cmd + A 全选？

因为 CLI 是**文字流**（像打字机），不是**文档**（像 Word）。
- 文档 = 可以随意选择、移动、删除
- CLI = 一行一行输入，只能用特殊快捷键

### 删除操作

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `Ctrl + U` | 删除光标前的所有内容 | 最常用！清空整行 |
| `Ctrl + K` | 删除光标后的所有内容 | 删除后半部分 |
| `Ctrl + W` | 删除光标前的一个单词 | 按单词删除 |
| `Ctrl + C` | 取消当前输入 | 放弃这行，重新开始 |
| `Option + Delete` | 删除光标前的一个单词 | Mac 风格删除 |

### 光标移动

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `Ctrl + A` | 跳到行首 | 快速回到开头 |
| `Ctrl + E` | 跳到行尾 | 快速跳到结尾 |
| `Option + ←` | 向左移动一个单词 | 按单词移动 |
| `Option + →` | 向右移动一个单词 | 按单词移动 |

### 历史命令

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `↑` | 上一条命令 | 查看历史 |
| `↓` | 下一条命令 | 向下翻历史 |
| `Ctrl + R` | 搜索历史命令 | 输入关键词搜索 |

### 其他常用

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `Tab` | 自动补全 | 补全文件名、命令 |
| `Ctrl + L` | 清屏 | 等同于 `clear` 命令 |
| `Ctrl + D` | 退出终端 | 等同于 `exit` |

### 最常用的三个：

1. **`Ctrl + U`** - 删除整行重新输入
2. **`Ctrl + A`** - 跳到行首
3. **`Ctrl + C`** - 取消当前命令

### 实战技巧

**场景1：输错了想重新输入**
```
$ cd /very/long/path/that/is/wrong
按 Ctrl + U → 整行删除
```

**场景2：想修改开头的命令**
```
$ cd /some/path
按 Ctrl + A → 跳到开头
改成：sudo cd /some/path
```

**场景3：命令卡住了**
```
$ python script.py
（程序一直运行）
按 Ctrl + C → 中断程序
```

  ### 如何验证是纯文本？

  在终端执行：
  ```bash
  file 文件名.py

  正确输出：
  api_clean.py: Python script text executable, ASCII text

  错误输出（RTF格式）：
  api_clean.py: Rich Text Format data

  记住

  - 📄 写文章 → Word
  - 💻 写代码 → VSCode
  - 📋 记笔记 → 备忘录

  编程代码必须用纯文本，富文本会带隐藏格式标记导致报错。

---

   前端每个页面包含4个文件：.wxml（结构）、.wxss（样式）、.js（逻辑）、.json（配置）