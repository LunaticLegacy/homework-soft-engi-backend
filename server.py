from fastapi import FastAPI, Depends
import json
import asyncio
from typing import Dict, Optional, Any
from modules.database import DatabaseManager, DBTimeoutError

from contextlib import asynccontextmanager

# --------------- 定义辅助函数 ------------------

# FastAPI app 实例
@asynccontextmanager
async def lifespan(app: FastAPI, db_manager: DatabaseManager):
    # 启动前：初始化连接池
    await db_manager.init_pool()
    print(" -------- Hello server! -------- ")
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

# 数据库管理器实例——只能有1个例。
config: Dict = load_config()
db_man: DatabaseManager = DatabaseManager(**config["database"])

def get_db_manager(config_path: str = "./config.json") -> DatabaseManager:
    global db_man
    return db_man

# 依赖注入示例
def get_db(db: DatabaseManager = Depends(get_db_manager)):
    return db

# ------------- 定义服务器 ------------
app = FastAPI(lifespan=lambda app: lifespan(app, db_man))
#
@app.get("/")
async def root():
    return {"message": "Hello, FastAPI is running!"}

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
    except ConnectionError:
        return {
            "Code": 401,
            "Message": "Failed in search for data: Database is not initialized.",
            "Result": None
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

@app.get("/register")
async def register(db: DatabaseManager = Depends(get_db)) -> Dict[str, Any]:

    try:
        conn = await db.get_connection(5.0)
        result: Optional[Dict[str, Any]] = await conn.fetchrow("SELECT * FROM users")
        return {
            "Code": 200,
            "Message": "Success in search for data.",
            "Result": result,
        }
        
    except:
        return {
            "Code": 401,
            "Message": "Failed in search for data: Unknown error.",
            "Result": None
        }

def run():
    print(" -------- Starting server... -------- ")
    import uvicorn

    global config
    global app
    global db_man
    
    server_config: Dict[str, Any] = config.get("server", {})
    uvicorn.run(
        "server:app", 
        **config["server"]
    )
    print(" -------- Server closed. -------- ")

# 启动 FastAPI
if __name__ == "__main__":
    run()
