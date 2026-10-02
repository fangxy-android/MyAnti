# 🐾 Codex Desktop Pet (代码桌宠)

> 类似于 OpenAI ChatGPT / Codex 桌面端的 **Codex Pets**，专为程序员与 AI 辅助编程打造的桌面状态可视化搭子！

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![PySide6](https://img.shields.io/badge/GUI-PySide6%20(Qt6)-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Cross--Platform-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## ✨ 核心特性

- 🖥️ **无边框透明悬浮窗**：支持置顶显示、任意拖拽、智能记忆窗口位置、高 DPI 像素点对点清晰渲染。
- 🐾 **5 款经典内置像素角色**：
  1. **整理鸭 Dewey**：Codex 经典鸭子搭子！头戴小绿帽，挥动小翅膀在微型笔记本上极速敲代码。
  2. **火焰精灵 Fireball**：Codex 招牌火焰精灵！动态火苗跳动，思考时化为幽蓝神火，编程时火花四溅。
  3. **赛博机人 CodeBot**：复古 CRT 显示器机器人，带有发光像素面部表情与机械臂。
  4. **赛博猫猫 Neko**：灵动黑白猫咪，尾巴轻轻摆动，爪子噼里啪啦敲键盘，完成后奖励小鱼干。
  5. **果冻史莱姆 Slime**：Q 弹青柠果冻，拥有可爱的挤压拉伸物理感，完成任务后头顶小皇冠。
- ⚡ **8 大 AI 工作状态可视化反馈**：
  - 😴 **待机 (Idle)**：轻松呼吸、灵动眨眼、四处张望。
  - 💭 **思考 (Thinking)**：托腮沉思、旋转齿轮、灯泡/问号微光。
  - ⚡ **编码中 (Working)**：微型笔记本展开，极速敲键，代码符号 `< / >` 向上迸发！
  - 🎉 **完成 (Done)**：欢呼雀跃，金色星星与彩带庆祝，胜利姿态。
  - ⚠️ **遇到错误 (Error)**：蚊香眼晕眩、冷汗滑落、BSOD 警示。
  - 🔔 **等待确认 (Waiting)**：敲击屏幕、向外挥手、感叹号等待提示。
  - 💖 **互动抚摸 (Clicked)**：点击桌宠脸颊泛红、冒出爱心气泡并欢快跳起。
  - 💤 **休眠 (Sleep)**：长时间无操作自动缩成一团呼呼大睡，Zzz 气泡飘动。
- 💬 **漫画风动态气泡 (Speech Bubble)**：悬浮在桌宠头顶，支持自动淡出、多种心情边框色彩（信息蓝/成功绿/警告橙/错误红）。
- 🎛️ **Codex 快捷控制台 (Quick Bar)**：
  - 单击桌宠互动，**双击桌宠**或右键即可一键呼出控制台抽屉。
  - 一键切换角色形象、测试状态动画、发送自定义气泡台词。
  - 🍅 **25分钟番茄专注钟**：开启后桌宠陪你一同全身心敲代码，专注倒计时结束桌宠播放胜利音乐欢呼并提醒休息！
- 🎵 **8-Bit 复古合成音效**：纯代码实时合成正弦/方波 8-bit 音效（按键声、完成音、警报声、爱心 chirp 等），无需外部音频文件，支持一键静音。
- 🌐 **本地 HTTP REST API & CLI 工具**：
  - 内置 `http://127.0.0.1:8765` REST 接口，任何外部工具（Antigravity、Cursor、Git 钩子、终端构建命令）均可轻松驱动桌宠！

---

## 🚀 快速启动

### 1. 运行依赖
本项目基于 Python 3.10+ 与 PySide6：
```bash
pip install PySide6 Pillow
```

### 2. 启动桌宠
- **方式一（快捷）**：直接双击运行根目录的 [`run.bat`](run.bat)
- **方式二（命令行）**：
  ```bash
  python main.py
  ```

---

## 🎮 交互指南

| 操作 | 动作效果 |
|---|---|
| **鼠标左键点击** | 触发抚摸互动（桌宠脸红、冒爱心、发出可爱音效、气泡问候） |
| **鼠标左键长按拖拽** | 移动桌宠到屏幕任意位置（松开自动保存位置） |
| **鼠标左键双击** | 呼出 / 隐藏 **Codex Quick Bar 控制台** |
| **鼠标右键单击** | 弹出功能菜单（形象切换、状态测试、尺寸缩放、置顶、音效、退出） |
| **系统托盘图标** | 左键单击托盘图标隐藏/显示桌宠；右键托盘图标管理全局菜单 |

---

## 🛠️ 外部集成与 CLI 控制 (pet-cli)

本项目配备了开箱即用的命令行控制工具 [`pet-cli.py`](pet-cli.py)，让你在任何终端或构建脚本中联动桌宠！

### 常用命令

```bash
# 查看桌宠当前状态
python pet-cli.py status

# 设置为正在工作状态（自动附带 5s 超时或自定义时长）
python pet-cli.py working "正在执行 npm run build..."
python pet-cli.py working "编译核心模块中..." --timeout 30

# 任务成功完成
python pet-cli.py done "构建完成！测试全数通过 🚀"

# 任务失败报警
python pet-cli.py error "编译失败！第 42 行语法错误"

# 让桌宠说一句话
python pet-cli.py say "记得多喝水、眨眨眼哦~"

# 切换角色形象 (dewey / fireball / codebot / neko / slime)
python pet-cli.py char fireball
```

### Git 提交联动 (Git Hook)

将 [`hooks/post-commit.sample`](hooks/post-commit.sample) 复制到你本地项目的 `.git/hooks/post-commit`：
```bash
cp hooks/post-commit.sample path/to/your/repo/.git/hooks/post-commit
chmod +x path/to/your/repo/.git/hooks/post-commit
```
每次你在该仓库执行 `git commit`，桌宠都会第一时间跳起欢呼庆祝！🎉

### PowerShell 快捷别名

将 [`hooks/Invoke-PetState.ps1`](hooks/Invoke-PetState.ps1) 引入你的 `$PROFILE`，即可在 PowerShell 中直接敲：
```powershell
pet-working "正在下载模型权重..."
pet-done "下载完成！"
pet-say "休息一下吧"
```

---

## 🌐 HTTP REST API 参考

桌宠内置 HTTP 服务器运行于 `http://127.0.0.1:8765`：

| 接口 | 方法 | 请求体 (JSON) | 说明 |
|---|---|---|---|
| `/api/status` | GET | 无 | 获取当前形象、状态及说明 |
| `/api/state` | POST | `{"state": "working", "text": "内容", "timeout": 5.0, "mood": "info"}` | 切换状态与提示词 |
| `/api/say` | POST | `{"message": "问候语", "mood": "success", "duration": 4.0}` | 弹出指定情绪的气泡 |
| `/api/character` | POST | `{"character": "dewey"}` | 切换当前桌宠形象 |
| `/api/action` | POST | `{"action": "click"}` / `{"action": "wake"}` / `{"action": "sleep"}` | 触发动作 |

---

## 📁 项目目录结构

```
MyAnti/
├── main.py                    # 应用程序主入口
├── config.py                  # 配置管理与持久化 (config.json)
├── test_pet.py                # 全面自动化测试套件
├── pet-cli.py                 # 外部命令行控制器
├── run.bat                    # Windows 一键启动脚本
├── engine/
│   ├── animation.py           # 逐帧动画引擎与刷新定时器
│   ├── pet_state.py           # 8 态状态机与自动超时恢复
│   └── sound.py               # 8-bit 复古合成音效与播放器
├── graphics/
│   ├── pixel_canvas.py        # 像素画布与清晰放大渲染器
│   └── characters/            # 5 大角色像素绘制与动作生成
│       ├── base.py            # 角色基类
│       ├── dewey.py           # 整理鸭 Dewey
│       ├── fireball.py        # 火焰精灵 Fireball
│       ├── codebot.py         # 赛博机人 CodeBot
│       ├── neko.py            # 赛博猫猫 Neko
│       └── slime.py           # 果冻史莱姆 Slime
├── ui/
│   ├── pet_window.py          # 无边框透明悬浮窗（拖拽、命中、右键菜单）
│   ├── speech_bubble.py       # 漫画风动态气泡控件
│   ├── quick_bar.py           # Codex 快捷控制台抽屉与番茄钟
│   └── tray_icon.py           # Windows 任务栏系统托盘管理
├── server/
│   ├── http_server.py         # 本地 HTTP REST API 服务
│   └── monitor.py             # 系统负载与自动休眠监视器
└── hooks/                     # Git Hook 与 PowerShell 辅助脚本
```
