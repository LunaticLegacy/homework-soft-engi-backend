from core.app import create_app

# 创建应用实例
app = create_app()

if __name__ == "__main__":
    import uvicorn
    from core.config import load_config
    
    # 加载配置
    config = load_config()
    server_config = config.get("server", {
        "host": "127.0.0.1",
        "port": 8000,
        "reload": True
    })
    
    # 运行应用
    uvicorn.run("app:app", **server_config)