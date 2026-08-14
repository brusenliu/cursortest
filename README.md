# 每日资讯整理机器人

在 VPS 上跑一个**只给你自己用**的 Telegram 机器人：每天 08:00（上海时间）抓取公开 RSS，去重、分类后推送摘要。占用内存很小，不占用 80/443，也不会改你现有的 nginx / sing-box。

## 它会做什么

- 拉取科技 / 国内 / 国际公开 RSS（失败的源自动跳过）
- 用 SQLite 按链接去重，避免同一条反复推送
- 每条只保留：标题、一句话摘要、来源、链接
- 可选：配置 `LLM_API_KEY` 后用 DeepSeek / OpenAI 兼容接口做二次整理

命令：

| 命令 | 作用 |
|------|------|
| `/start` | 确认当前聊天是否已授权；若还没填 chat id，会把 id 发给你 |
| `/today` | 立刻生成并发送一份今日摘要 |
| `/sources` | 列出当前 RSS 源 |
| `/ping` | 探活 |

源列表在 [`newsbot/feeds.yaml`](newsbot/feeds.yaml)，默认包括：

- 科技：Hacker News、Solidot、少数派
- 国内：36氪、IT之家、新浪国内
- 国际：BBC World、NPR News

改完后重启服务即可。

## 1. 向 BotFather 申请 Token

1. 用 Telegram 打开 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot`，按提示起名
3. 记下发给你的 token（形如 `123456:ABC...`）
4. 先给新机器人发一条 `/start`（后面部署完成即可用）

Token 只写在服务器 `/etc/newsbot.env`，**不要提交进 git，也不要发到聊天里。**

## 2. 部署到 Ubuntu

在项目目录以 root 执行：

```bash
chmod +x deploy/install.sh
sudo ./deploy/install.sh
```

脚本会：

- 创建系统用户 `newsbot`
- 把代码放到 `/opt/newsbot` 并建立 venv
- 若 `/etc/newsbot.env` 不存在则生成模板
- token 已填写时启用 `systemd` 服务 `newsbot`

编辑环境变量：

```bash
sudo nano /etc/newsbot.env
```

```
TELEGRAM_BOT_TOKEN=你的token
TELEGRAM_CHAT_ID=
TZ=Asia/Shanghai
NEWSBOT_DB=/var/lib/newsbot/seen.sqlite
LLM_API_KEY=
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

`TELEGRAM_CHAT_ID` 可以先留空。启动服务后给机器人发 `/start`，它会回复你的 chat id，再填回去并重启：

```bash
sudo systemctl restart newsbot
```

本地不连 Telegram、只看摘要长什么样：

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m newsbot --print
```

## 3. 验收

- `systemctl status newsbot` 为 active
- Telegram 里 `/ping` 返回 `pong`
- `/today` 能收到分类摘要
- 第二天 08:00 会自动再推一份

日志：

```bash
journalctl -u newsbot -f
```

## 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `TELEGRAM_BOT_TOKEN` | 是 | BotFather 发的 token |
| `TELEGRAM_CHAT_ID` | 推送时需要 | 只允许这些聊天使用命令并接收日报，逗号分隔 |
| `TZ` | 否 | 默认 `Asia/Shanghai` |
| `NEWSBOT_DB` | 否 | SQLite 路径，默认 `/var/lib/newsbot/seen.sqlite` |
| `NEWSBOT_FEEDS` | 否 | 自定义 `feeds.yaml` 路径 |
| `LLM_API_KEY` | 否 | 配了才调用大模型整理摘要 |
| `LLM_BASE_URL` | 否 | 默认 `https://api.deepseek.com` |
| `LLM_MODEL` | 否 | 默认 `deepseek-chat` |
