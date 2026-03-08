### 3. 路由与API版本控制

**核心作用**：处理HTTP请求，支持API版本控制，实现路由与业务逻辑分离

**设计特点**：
- 支持URL路径版本控制
- 支持Header版本控制
- 路由自动注册
- 支持路由分组

**模块架构图**：
```mermaid
graph LR
    A[主API路由器] --> B[版本路由v1]
    A --> C[版本路由v2]
    B --> D[资源路由1]
    B --> E[资源路由2]
    C --> F[资源路由1]
    C --> G[资源路由2]
    D --> H[路径参数处理]
    E --> I[查询参数处理]
    F --> J[路径参数处理]
    G --> K[查询参数处理]
    
    style A fill:#FF6B6B,stroke:#2D3436,stroke-width:3px,color:white,rx:8,ry:8
    style B fill:#4ECDC4,stroke:#2D3436,stroke-width:2px,color:#2D3436,rx:8,ry:8
    style C fill:#45B7D1,stroke:#2D3436,stroke-width:2px,color:white,rx:8,ry:8
    style D fill:#96CEB4,stroke:#2D3436,stroke-width:2px,color:#2D3436,rx:8,ry:8
    style E fill:#FF9FF3,stroke:#2D3436,stroke-width:2px,color:#2D3436,rx:8,ry:8
    style F fill:#96CEB4,stroke:#2D3436,stroke-width:2px,color:#2D3436,rx:8,ry:8
    style G fill:#FF9FF3,stroke:#2D3436,stroke-width:2px,color:#2D3436,rx:8,ry:8
    style H fill:#54A0FF,stroke:#2D3436,stroke-width:2px,color:white,rx:8,ry:8
    style I fill:#FECA57,stroke:#2D3436,stroke-width:2px,color:#2D3436,rx:8,ry:8
    style J fill:#54A0FF,stroke:#2D3436,stroke-width:2px,color:white,rx:8,ry:8
    style K fill:#FECA57,stroke:#2D3436,stroke-width:2px,color:#2D3436,rx:8,ry:8
```

**数据流转图**：
```mermaid
sequenceDiagram
    participant Client as 客户端
    participant APIRouter as 主API路由器
    participant VersionRouter as 版本路由
    participant ResourceRouter as 资源路由
    participant PathHandler as 路径参数处理
    participant QueryHandler as 查询参数处理
    participant Service as 服务层
    
    Client->>APIRouter: 发送请求
    APIRouter->>VersionRouter: 路由到版本
    VersionRouter->>ResourceRouter: 路由到资源
    ResourceRouter->>PathHandler: 处理路径参数
    ResourceRouter->>QueryHandler: 处理查询参数
    PathHandler->>Service: 传递参数
    QueryHandler->>Service: 传递参数
    Service->>Client: 返回响应
```

**关键实现**：
```python
# app/api/__init__.py
from fastapi import APIRouter
from app.api.v1 import api_router as v1_router
from app.api.v2 import api_router as v2_router

# 主API路由器
api_router = APIRouter(prefix="/api")

# 注册版本路由
api_router.include_router(v1_router, prefix="/v1", tags=["v1"])
api_router.include_router(v2_router, prefix="/v2", tags=["v2"])
```