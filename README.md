# 每日资讯整理机器人

在 VPS 上每天 08:00（上海时间）抓取公开 RSS，去重分类后把摘要发到你的**邮箱**。也可以同时开 Telegram。占用内存很小，不占用 80/443，不改 nginx / sing-box。

## 它会做什么

- 拉取科技 / 国内 / 国际公开 RSS（失败的源自动跳过）
- 用 SQLite 按链接去重，避免同一条反复推送
- 每条只保留：标题、一句话摘要、来源、链接
- 邮件用分区排版（科技 / 国内 / 国际），并附纯文本备份
- 默认发邮件；配了 Telegram token 也可以再推一份

源列表在 [`newsbot/feeds.yaml`](newsbot/feeds.yaml)，默认包括：

- 科技：Hacker News、Solidot、少数派
- 国内：36氪、IT之家、新浪国内
- 国际：BBC World、NPR News

## 1. 准备发信邮箱

常用做法是**用自己的邮箱给自己发**。国内邮箱请用「授权码」，不要用登录密码。

| 邮箱 | SMTP | 怎么拿授权码 |
|------|------|----------------|
| QQ / Foxmail | `smtp.qq.com:465` | QQ 邮箱 → 设置 → 账户 → 开启 SMTP → 生成授权码 |
| 163 | `smtp.163.com:465` | 设置 → POP3/SMTP/IMAP → 授权码 |
| Gmail | `smtp.gmail.com:587` | 账号开启两步验证后，生成 [应用专用密码](https://myaccount.google.com/apppasswords) |

`SMTP_HOST` 一般可以留空，程序会按邮箱域名自动推断。

## 2. 部署到 Ubuntu

```bash
chmod +x deploy/install.sh
sudo ./deploy/install.sh
sudo nano /etc/newsbot.env
```

至少填写：

```
MAIL_TO=you@example.com
SMTP_PASSWORD=授权码或应用专用密码
TZ=Asia/Shanghai
NEWSBOT_DB=/var/lib/newsbot/seen.sqlite
```

`SMTP_USER` / `SMTP_FROM` 默认等于 `MAIL_TO`。然后：

```bash
sudo systemctl enable --now newsbot
```

立刻发一封测试：

```bash
cd /opt/newsbot
sudo -u newsbot /opt/newsbot/.venv/bin/python -m newsbot --send
```

只预览、不发送：

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m newsbot --print
```

## 3. 验收

- `systemctl status newsbot` 为 active
- `--send` 后收件箱里有「每日资讯 YYYY-MM-DD」
- 第二天 08:00 会再自动发一封

日志：

```bash
journalctl -u newsbot -f
```

## 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `MAIL_TO` | 发邮件时必填 | 收件人，多个用逗号分隔 |
| `SMTP_PASSWORD` | 发邮件时必填 | 授权码 / 应用专用密码 |
| `SMTP_USER` | 否 | 默认等于 `MAIL_TO` |
| `SMTP_FROM` | 否 | 默认等于 `SMTP_USER` |
| `SMTP_HOST` | 否 | 一般可留空，自动按邮箱推断 |
| `SMTP_PORT` | 否 | 465（SSL）或 587（STARTTLS） |
| `SMTP_SECURITY` | 否 | `ssl` 或 `starttls` |
| `TELEGRAM_BOT_TOKEN` | 否 | 同时推 Telegram 时才需要 |
| `TELEGRAM_CHAT_ID` | 否 | Telegram 收件聊天 |
| `TZ` | 否 | 默认 `Asia/Shanghai` |
| `NEWSBOT_DB` | 否 | SQLite 路径 |
| `LLM_API_KEY` | 否 | 配了才调用大模型整理摘要 |

Telegram 仍可用：给 [@BotFather](https://t.me/BotFather) 申请 token 后填进 env，服务会同时轮询 Telegram。
