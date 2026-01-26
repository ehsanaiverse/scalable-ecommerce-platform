from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.src.db.database import get_db
from app.src.models.user import User as UserModel
from app.src.core.security import required_role
from app.src.schemas.products import Product as ProductSchema, ProductUpdate
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

    return {'message': 'Product added successfully'}


@router.put('/admin/update-product/{product_id}')
def update_product(product_id: int, product: ProductSchema, db: Session = Depends(get_db), current_user: dict = Depends(required_role('admin'))):
    existing_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()

    if not existing_product:
        return {'message': 'Product not found'}

    existing_product.name = product.name
    existing_product.description = product.description
    existing_product.price = product.price
    existing_product.category = product.category
    existing_product.stock_quantity = product.stock_quantity

    db.add(existing_product)
    db.commit()
    db.refresh(existing_product)

    return {'message': 'Product updated successfully'}



@router.delete('/admin/delete-product/{product_id}')
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: dict = Depends(required_role('admin'))):
    existing_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()

    if not existing_product:
        return {'message': 'Product not found'}

    db.delete(existing_product)
    db.commit()

    return {'message': 'Product deleted successfully'}
    