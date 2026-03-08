# 数据库示例

本示例展示如何使用FastAPI企业级框架模板的数据库抽象层，包括数据库模型定义、仓储模式、事务管理等。

## 目录结构

```
examples/database/
├── main.py              # 应用入口文件
├── models.py            # 数据库模型
├── schemas.py           # Pydantic数据模型
├── repositories.py      # 仓储层实现
├── services.py          # 服务层实现
├── dependencies.py      # 依赖注入
├── requirements.txt     # 依赖列表
└── README.md            # 本文件
```

## 功能说明

本示例实现了一个简单的产品管理系统，包含以下功能：
- 产品CRUD操作
- 仓储模式实现
- 事务管理
- 复杂查询示例
- 多表关联查询

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python main.py
```

### 3. 测试数据库功能

使用API文档测试以下功能：
- 创建产品
- 获取产品列表
- 获取单个产品
- 更新产品
- 删除产品
- 复杂查询（按类别、价格范围等）

## 示例代码

### main.py

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.config.settings import app_settings
from app.middleware import setup_cors
from .models import Base, Product, Category
from .schemas import (
    ProductCreate, ProductUpdate, Product as ProductSchema,
    CategoryCreate, Category as CategorySchema
)
from .services import ProductService, CategoryService
from .dependencies import get_db, get_product_service, get_category_service

# 创建FastAPI应用
app = FastAPI(
    title=app_settings.APP_NAME,
    version=app_settings.APP_VERSION,
    openapi_url=f"{app_settings.API_V1_STR}/openapi.json",
)

# 设置CORS中间件
setup_cors(app)

# 初始化数据库
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=next(get_db()).bind)

# 类别路由
@app.post(f"{app_settings.API_V1_STR}/categories", response_model=CategorySchema)
def create_category(
    category: CategoryCreate,
    category_service: CategoryService = Depends(get_category_service)
):
    """创建类别"""
    return category_service.create_category(category)

@app.get(f"{app_settings.API_V1_STR}/categories", response_model=List[CategorySchema])
def get_categories(
    skip: int = 0,
    limit: int = 100,
    category_service: CategoryService = Depends(get_category_service)
):
    """获取类别列表"""
    return category_service.get_categories(skip=skip, limit=limit)

# 产品路由
@app.post(f"{app_settings.API_V1_STR}/products", response_model=ProductSchema)
def create_product(
    product: ProductCreate,
    product_service: ProductService = Depends(get_product_service)
):
    """创建产品"""
    return product_service.create_product(product)

@app.get(f"{app_settings.API_V1_STR}/products", response_model=List[ProductSchema])
def get_products(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    product_service: ProductService = Depends(get_product_service)
):
    """获取产品列表，支持按类别和价格筛选"""
    return product_service.get_products(
        skip=skip, 
        limit=limit, 
        category_id=category_id,
        min_price=min_price,
        max_price=max_price
    )

@app.get(f"{app_settings.API_V1_STR}/products/{int}:id", response_model=ProductSchema)
def get_product(
    id: int,
    product_service: ProductService = Depends(get_product_service)
):
    """获取单个产品"""
    product = product_service.get_product(id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put(f"{app_settings.API_V1_STR}/products/{int}:id", response_model=ProductSchema)
def update_product(
    id: int,
    product: ProductUpdate,
    product_service: ProductService = Depends(get_product_service)
):
    """更新产品"""
    return product_service.update_product(id, product)

@app.delete(f"{app_settings.API_V1_STR}/products/{int}:id")
def delete_product(
    id: int,
    product_service: ProductService = Depends(get_product_service)
):
    """删除产品"""
    product_service.delete_product(id)
    return {"message": "Product deleted successfully"}

# 根路径
@app.get("/")
def root():
    """根路径"""
    return {
        "message": "Welcome to FastAPI Enterprise Architecture - Database Example",
        "version": app_settings.APP_VERSION,
        "api_v1": app_settings.API_V1_STR,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

### models.py

```python
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    category = relationship("Category", back_populates="products")
```

### schemas.py

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# 类别Schema
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# 产品Schema
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., gt=0)
    stock: int = Field(0, ge=0)
    category_id: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = None

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    category: Category

    class Config:
        orm_mode = True
```

### repositories.py

```python
from sqlalchemy.orm import Session
from typing import List, Optional
from .models import Product, Category
from .schemas import ProductCreate, ProductUpdate, CategoryCreate, CategoryUpdate

class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, category: CategoryCreate) -> Category:
        """创建类别"""
        db_category = Category(**category.dict())
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Category]:
        """获取所有类别"""
        return self.db.query(Category).offset(skip).limit(limit).all()
    
    def get_by_id(self, id: int) -> Optional[Category]:
        """根据ID获取类别"""
        return self.db.query(Category).filter(Category.id == id).first()
    
    def update(self, category: Category, category_update: CategoryUpdate) -> Category:
        """更新类别"""
        update_data = category_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        self.db.commit()
        self.db.refresh(category)
        return category
    
    def delete(self, category: Category) -> None:
        """删除类别"""
        self.db.delete(category)
        self.db.commit()

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, product: ProductCreate) -> Product:
        """创建产品"""
        db_product = Product(**product.dict())
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product
    
    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[Product]:
        """获取所有产品，支持筛选"""
        query = self.db.query(Product)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if min_price:
            query = query.filter(Product.price >= min_price)
        if max_price:
            query = query.filter(Product.price <= max_price)
        
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, id: int) -> Optional[Product]:
        """根据ID获取产品"""
        return self.db.query(Product).filter(Product.id == id).first()
    
    def update(self, product: Product, product_update: ProductUpdate) -> Product:
        """更新产品"""
        update_data = product_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def delete(self, product: Product) -> None:
        """删除产品"""
        self.db.delete(product)
        self.db.commit()
    
    def get_products_with_low_stock(self, threshold: int = 10) -> List[Product]:
        """获取库存不足的产品"""
        return self.db.query(Product).filter(Product.stock < threshold).all()
```

### services.py

```python
from typing import List, Optional
from .repositories import ProductRepository, CategoryRepository
from .schemas import ProductCreate, ProductUpdate, CategoryCreate, CategoryUpdate
from .models import Product, Category

class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo
    
    def create_category(self, category: CategoryCreate) -> Category:
        """创建类别"""
        return self.category_repo.create(category)
    
    def get_categories(self, skip: int = 0, limit: int = 100) -> List[Category]:
        """获取类别列表"""
        return self.category_repo.get_all(skip, limit)
    
    def get_category(self, id: int) -> Optional[Category]:
        """获取单个类别"""
        return self.category_repo.get_by_id(id)

class ProductService:
    def __init__(self, product_repo: ProductRepository, category_repo: CategoryRepository):
        self.product_repo = product_repo
        self.category_repo = category_repo
    
    def create_product(self, product: ProductCreate) -> Product:
        """创建产品"""
        # 验证类别是否存在
        category = self.category_repo.get_by_id(product.category_id)
        if not category:
            raise ValueError(f"Category with id {product.category_id} not found")
        
        return self.product_repo.create(product)
    
    def get_products(
        self, 
        skip: int = 0, 
        limit: int = 100,
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[Product]:
        """获取产品列表"""
        return self.product_repo.get_all(skip, limit, category_id, min_price, max_price)
    
    def get_product(self, id: int) -> Optional[Product]:
        """获取单个产品"""
        return self.product_repo.get_by_id(id)
    
    def update_product(self, id: int, product_update: ProductUpdate) -> Product:
        """更新产品"""
        product = self.product_repo.get_by_id(id)
        if not product:
            raise ValueError(f"Product with id {id} not found")
        
        # 如果更新了类别，验证类别是否存在
        if product_update.category_id:
            category = self.category_repo.get_by_id(product_update.category_id)
            if not category:
                raise ValueError(f"Category with id {product_update.category_id} not found")
        
        return self.product_repo.update(product, product_update)
    
    def delete_product(self, id: int) -> None:
        """删除产品"""
        product = self.product_repo.get_by_id(id)
        if not product:
            raise ValueError(f"Product with id {id} not found")
        
        self.product_repo.delete(product)
    
    def get_low_stock_products(self, threshold: int = 10) -> List[Product]:
        """获取库存不足的产品"""
        return self.product_repo.get_products_with_low_stock(threshold)
```

### dependencies.py

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .repositories import ProductRepository, CategoryRepository
from .services import ProductService, CategoryService

# 创建SQLite数据库引擎
SQLALCHEMY_DATABASE_URL = "sqlite:///./database_example.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建数据库会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 数据库依赖
def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 仓储依赖
def get_product_repository(db: Session = Depends(get_db)) -> ProductRepository:
    """获取产品仓储"""
    return ProductRepository(db)

def get_category_repository(db: Session = Depends(get_db)) -> CategoryRepository:
    """获取类别仓储"""
    return CategoryRepository(db)

# 服务依赖
def get_product_service(
    product_repo: ProductRepository = Depends(get_product_repository),
    category_repo: CategoryRepository = Depends(get_category_repository)
) -> ProductService:
    """获取产品服务"""
    return ProductService(product_repo, category_repo)

def get_category_service(
    category_repo: CategoryRepository = Depends(get_category_repository)
) -> CategoryService:
    """获取类别服务"""
    return CategoryService(category_repo)
```

### requirements.txt

```
fastapi
uvicorn
pydantic
sqlalchemy
```

## 核心概念说明

1. **仓储模式**：将数据访问逻辑封装在仓储层，实现业务逻辑与数据访问分离
2. **服务层**：封装业务逻辑，协调多个仓储操作
3. **依赖注入**：使用FastAPI的依赖注入系统管理对象生命周期
4. **事务管理**：通过数据库会话实现事务控制
5. **数据验证**：使用Pydantic进行数据验证和序列化
6. **多表关联**：实现了产品和类别之间的一对多关联

## 下一步

- 查看[事件示例](../events/README.md)：了解如何使用事件总线
- 查看[中间件示例](../middleware/README.md)：了解如何使用自定义中间件
- 查看[配置示例](../config/README.md)：了解如何使用配置管理
