from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

# 本地启动命令：～/Documents/AI/ai-journey/.venv/bin/python -m uvicorn main:app --reload --app-dir demos/fastAPI


# 定义用户模型
class User(BaseModel):
    name: str
    email: str
    password: str


items: Dict[int, User] = {}
next_id = 1


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "Users"}


@app.get("/users/{item_id}")
def read_item(item_id: int, q: str | None = None):
    if item_id not in items:
        return {"error": "用户不存在"}
    return items[item_id]


@app.post("/users")
def create_user(user: User):
    global next_id
    items[next_id] = user
    next_id += 1
    return {"message": "用户创建成功", "user": user}

# PUT 路由 - 更新数据


@app.put("/users/{user_id}")
def update_user(user_id: int, user: User):
    if user_id not in items:
        return {"error": "用户不存在"}
    items[user_id] = user
    return items[user_id]
# DELETE 路由 - 删除数据


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    if user_id not in items:
        return {"error": "用户不存在"}
    del items[user_id]
    return {"message": f"用户 {user_id} 已删除"}
