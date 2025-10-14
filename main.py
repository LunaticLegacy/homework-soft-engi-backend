from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

# 创建 FastAPI 实例
app = FastAPI(
    title="示例API",
    description="FastAPI基础功能演示",
    version="1.0.0"
)

# 定义请求体模型
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

# 内存数据库模拟
items = {
    1: {"name": "苹果", "price": 5.5},
    2: {"name": "香蕉", "price": 3.2},
    3: {"name": "橙子", "price": 4.8}
}

# 根路径
@app.get("/")
def read_root():
    return {"message": "欢迎使用FastAPI示例"}

# 带路径参数的路由
@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="商品不存在")
    return items[item_id]

# 带查询参数的路由
@app.get("/search/")
def search_items(q: Optional[str] = Query(None, min_length=2, max_length=10)):
    if q is None:
        return {"results": list(items.values())}
    results = [item for item in items.values() if q.lower() in item["name"].lower()]
    return {"results": results}

# POST 请求处理
@app.post("/items/")
def create_item(item: Item):
    item_id = max(items.keys()) + 1
    items[item_id] = item.dict()
    return {"item_id": item_id, **item.dict()}

# 自定义异常处理
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"message": "值错误: " + str(exc)}
    )

# 启动命令 (在文件末尾添加)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)