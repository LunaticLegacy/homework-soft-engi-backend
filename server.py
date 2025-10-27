from fastapi import FastAPI, Depends
import json
from typing import Dict
from modules.database import DatabaseManager

from contextlib import asynccontextmanager

# FastAPI app 实例
@asynccontextmanager
async def lifespan(app: FastAPI, db_manager: DatabaseManager):
    # 启动前：初始化连接池
    await db_manager.init_pool()
    try:
        yield
    finally:
        # 关闭时：释放连接池
        await db_manager.close_all_connections()


app = FastAPI()


# 配置加载
def load_config(json_config_path: str = "./config.json") -> Dict:
    with open(json_config_path, "r") as f:
        config = json.load(f)
    return config

# 数据库管理器实例
def get_db_manager(config_path: str = "./config.json") -> DatabaseManager:
    config = load_config(config_path)
    db_config = config.get("database", {})
    return DatabaseManager(**db_config)

# 依赖注入示例
def get_db(db: DatabaseManager = Depends(get_db_manager)):
    return db

# FastAPI路由示例
@app.get("/users")
async def read_users(db: DatabaseManager = Depends(get_db)):
    pass

# 启动 FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
