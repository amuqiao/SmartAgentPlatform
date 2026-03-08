# 快速入门示例

本示例展示如何使用FastAPI企业级框架模板创建一个简单的API应用。

## 目录结构

```
examples/quickstart/
├── main.py              # 应用入口文件
├── requirements.txt     # 依赖列表
└── README.md            # 本文件
```

## 功能说明

本示例创建一个简单的待办事项API，包含以下功能：
- 获取待办事项列表
- 创建新的待办事项
- 获取单个待办事项
- 更新待办事项
- 删除待办事项

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python main.py
```

### 3. 访问API文档

打开浏览器访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 示例代码

### main.py

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.config.settings import app_settings
from app.middleware import setup_cors

# 创建FastAPI应用
app = FastAPI(
    title=app_settings.APP_NAME,
    version=app_settings.APP_VERSION,
    openapi_url=f"{app_settings.API_V1_STR}/openapi.json",
)

# 设置CORS中间件
setup_cors(app)

# 数据模型
class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TodoCreate(TodoBase):
    pass

class TodoUpdate(TodoBase):
    pass

class Todo(TodoBase):
    id: int

    class Config:
        orm_mode = True

# 模拟数据库
todos_db = [
    Todo(id=1, title="学习FastAPI", description="掌握FastAPI的核心概念", completed=False),
    Todo(id=2, title="编写示例", description="创建各种场景的示例代码", completed=False),
]

# API路由
@app.get(f"{app_settings.API_V1_STR}/todos", response_model=List[Todo])
def get_todos():
    """获取待办事项列表"""
    return todos_db

@app.post(f"{app_settings.API_V1_STR}/todos", response_model=Todo)
def create_todo(todo: TodoCreate):
    """创建新的待办事项"""
    new_todo = Todo(
        id=len(todos_db) + 1,
        title=todo.title,
        description=todo.description,
        completed=todo.completed
    )
    todos_db.append(new_todo)
    return new_todo

@app.get(f"{app_settings.API_V1_STR}/todos/{int}:id", response_model=Todo)
def get_todo(id: int):
    """获取单个待办事项"""
    for todo in todos_db:
        if todo.id == id:
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.put(f"{app_settings.API_V1_STR}/todos/{int}:id", response_model=Todo)
def update_todo(id: int, todo: TodoUpdate):
    """更新待办事项"""
    for index, existing_todo in enumerate(todos_db):
        if existing_todo.id == id:
            updated_todo = existing_todo.copy(
                update={
                    "title": todo.title,
                    "description": todo.description,
                    "completed": todo.completed
                }
            )
            todos_db[index] = updated_todo
            return updated_todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete(f"{app_settings.API_V1_STR}/todos/{int}:id")
def delete_todo(id: int):
    """删除待办事项"""
    for index, existing_todo in enumerate(todos_db):
        if existing_todo.id == id:
            todos_db.pop(index)
            return {"message": "Todo deleted successfully"}
    raise HTTPException(status_code=404, detail="Todo not found")

# 根路径
@app.get("/")
def root():
    """根路径"""
    return {
        "message": "Welcome to FastAPI Enterprise Architecture",
        "version": app_settings.APP_VERSION,
        "api_v1": app_settings.API_V1_STR,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

### requirements.txt

```
fastapi
uvicorn
pydantic
```

## 核心概念说明

1. **应用创建**：使用FastAPI类创建应用实例，配置基本信息
2. **中间件设置**：使用内置的CORS中间件配置跨域请求
3. **数据模型**：使用Pydantic定义数据模型，实现数据验证
4. **API路由**：使用装饰器定义API端点，支持多种HTTP方法
5. **配置管理**：使用内置的配置管理模块获取应用配置

## 下一步

- 查看[认证示例](../auth/README.md)：了解如何使用内置的认证功能
- 查看[数据库示例](../database/README.md)：了解如何使用数据库抽象层
- 查看[事件示例](../events/README.md)：了解如何使用事件总线
