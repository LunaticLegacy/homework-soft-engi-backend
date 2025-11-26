from core.app import create_app

# 创建应用实例
app = create_app()

if __name__ == "__main__":
    import uvicorn
    # 加载配置
    from core.config import get_settings
    config = get_settings()
    server_config = {
        "host": config.server.host,
        "port": config.server.port,
        "reload": config.server.reload
    }
    
    # 获取SSL配置
    ssl_keyfile = config.ssl.keyfile
    ssl_certfile = config.ssl.certfile
    
    # 运行应用
    if ssl_keyfile and ssl_certfile:
        # 如果有证书，则运行https
        uvicorn.run(
            "app:app", 
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            **server_config
        )
    else:   # 否则http
        uvicorn.run("app:app", **server_config)
