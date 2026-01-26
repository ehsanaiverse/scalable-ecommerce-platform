from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.src.db.database import get_db
from app.src.models.user import User as UserModel
from app.src.core.security import required_role
from app.src.schemas.products import Product as ProductSchema
from app.src.models.products import Product as ProductModel

router = APIRouter(tags=['Products'])

@router.get('/products')
def get_products(db: Session = Depends(get_db)):
    products = db.query(ProductModel).all()
    if not products:
        return {'message': 'No products found'}
    return products


@router.post('/admin/add-product')
def add_product(product: ProductSchema, db: Session = Depends(get_db), current_user: dict = Depends(required_role('admin'))):
    existing_product = db.query(ProductModel).filter(ProductModel.name == product.name).first()

    if existing_product:
        return {'message': 'Product with this name already exists'}

    new_product = ProductModel(
        name=product.name,
        description=product.description,
        price=product.price,
        category=product.category,
        stock_quantity=product.stock_quantity
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product