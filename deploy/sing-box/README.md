# 新加坡节点：AnyTLS + Reality（sing-box）

仅 TCP 443，对外表现与访问 `www.samsung.com` 一致。不需要域名、不需要证书、不开放 80。

本目录只有不含密钥的模板。真实配置与凭据只存在于目标机：

| 文件 | 说明 |
|------|------|
| `/etc/sing-box/config.json` | 服务端配置（`server.template.json` 填值后的结果） |
| `/etc/sing-box/credentials.env` | 私钥、密码、short_id、分享链接，`chmod 600` |
| `~ubuntu/sg-client.json` | 可直接导入 sing-box 系客户端的配置 |
| `~ubuntu/sg-credentials.env` | 同 credentials.env 的副本，供 `scp` 取用 |

## 已部署环境

- sing-box 1.14.3（官方 `.deb`，systemd 以 `sing-box` 用户运行）
- BBR + fq：`/etc/sysctl.d/99-bbr.conf`
- ufw：仅放行 TCP 22 / TCP 443

## 为什么选这套

- **Reality**：没有正确密钥的连接原样转发到握手目标 `www.samsung.com:443`，探测方拿到的是真实证书和 301 到 `/sg/`，与直接访问该站一致。
- **AnyTLS**：在 TLS 之上做长度填充，削弱「TLS 套 TLS」特征；旧节点的 VLESS Reality 没有这层。
- **握手目标**从新加坡机器实测：Akamai 新加坡边缘节点，TCP 握手约 34 ms，TLS 1.3 / H2 / X25519 齐全。

## 客户端

AnyTLS 需要 sing-box 系客户端：sing-box 官方 App（SFA / SFI / SFM）、Hiddify、Karing、NekoBox。
**Clash Verge / mihomo / Stash 不支持**。

导入方式二选一：

1. 取回 JSON：`scp ubuntu@<server>:~/sg-client.json .`，导入 sing-box App。
2. 用 `sg-credentials.env` 里的 `SHARE_URI`（`anytls://...` 链接）扫码或粘贴到 Hiddify / Karing。

## 重新生成凭据

```bash
sing-box generate reality-keypair      # PrivateKey / PublicKey
sing-box generate rand 8 --hex         # short_id
sing-box generate rand 24 --base64     # AnyTLS 密码
sing-box check -C /etc/sing-box && systemctl restart sing-box
```

## 验收命令

```bash
# 服务端
systemctl is-active sing-box && ss -lntp | grep ':443 '
# 任意外部机器：无密钥探测应看到 Samsung 证书并 301 到 /sg/
curl -sk --resolve www.samsung.com:443:<server>:443 -o /dev/null -w '%{http_code} %{redirect_url}\n' https://www.samsung.com/
```

## 更换握手目标

握手目标必须支持 TLS 1.3、HTTP/2、X25519，并且离服务器近。在服务器上测试：

```bash
echo | openssl s_client -connect <host>:443 -servername <host> -tls1_3 -alpn h2 2>/dev/null | grep -E 'Temp Key|ALPN'
curl -s -o /dev/null -w '%{time_connect}\n' https://<host>/
```

然后同时改服务端 `server_name` / `handshake.server` 和客户端 `server_name`，重启服务。
