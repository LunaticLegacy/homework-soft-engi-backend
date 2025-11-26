## certs

这里是放置证书的地方。
- HTTPS协议**必须**拥有证书才可运行。
- 请自行生成`key.pem`和`cert.pem`：

```powershell
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=CN/ST=State/L=City/O=Organization/CN=localhost"
```


