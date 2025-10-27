from fastapi import FastAPI, Depends
import json
import asyncio
from typing import Dict, Optional, Any
from modules.database import DatabaseManager, DBTimeoutError

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


# ------------- 定义服务器的位置 ------------
config: Dict = load_config()
db_man: DatabaseManager = DatabaseManager(**config["database"])
app = FastAPI(lifespan=lambda app: lifespan(app, db_man))

# FastAPI路由示例
@app.get("/users")
async def read_users(db: DatabaseManager = Depends(get_db)) -> Dict[str, Any]:
    try:
        conn = await db.get_connection(5.0)
        result: Optional[Dict[str, Any]] = await conn.fetchrow("SELECT * FROM users")
        return {
            "Code": 200,
            "Message": "Success in search for data.",
            "Result": result,
        }
    except DBTimeoutError:
        return {
            "Code": 401,
            "Message": "Failed in search for data: Timeout.",
            "Result": None
        }
    except:
        return {
            "Code": 401,
            "Message": "Failed in search for data: Unknown error.",
            "Result": None
        }

def run():
    import uvicorn    
    global app
    global db_man
    uvicorn.run(
        "server:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
    )

# 启动 FastAPI
if __name__ == "__main__":
    run()
