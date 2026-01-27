from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.src.db.database import get_db
from app.src.models.user import User as UserModel
from app.src.core.security import required_role
from app.src.schemas.products import ProductCreate, ProductUpdate, ProductResponse
from app.src.models.products import Product as ProductModel
from app.src.models.category import Category as CategoryModel
from app.src.models.inventory import Inventory as InventoryModel

router = APIRouter(tags=['Products'])

@router.get('/products', response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    products = db.query(ProductModel).all()
    if not products:
        return []
    return products


@router.post('/admin/add-product', response_model=ProductResponse)
def add_product(product: ProductCreate, db: Session = Depends(get_db), current_user: dict = Depends(required_role('admin'))):
    # Check if category exists
    category_check = db.query(CategoryModel).filter(CategoryModel.id == product.category_id).first()
    if not category_check:
        raise HTTPException(status_code=400, detail='Category not found')

    existing_product = db.query(ProductModel).filter(ProductModel.name == product.name).first()
    if existing_product:
        raise HTTPException(status_code=400, detail='Product with this name already exists')

    new_product = ProductModel(
        name=product.name,
        description=product.description,
        price=product.price,
        category_id=product.category_id
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    # Initialize Inventory
    new_inventory = InventoryModel(
        product_id=new_product.id,
        stock_quantity=product.stock_quantity
    )
    db.add(new_inventory)
    db.commit()

    return new_product

@router.put('/admin/update-product/{product_id}', response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(required_role('admin'))
):
    existing_product = db.query(ProductModel).filter(
        ProductModel.id == product_id
    ).first()

    if not existing_product:
        raise HTTPException(status_code=404, detail='Product not found')

    update_data = product.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    if "category_id" in update_data and update_data["category_id"] is not None:
        category = db.query(CategoryModel).filter(
            CategoryModel.id == update_data["category_id"]
        ).first()

        if not category:
            raise HTTPException(
                status_code=400,
                detail="Invalid category_id"
            )

    for field, value in update_data.items():
        if value is None:
            continue
        if isinstance(value, str) and value.strip() == "":
            continue
        setattr(existing_product, field, value)


    db.commit()
    db.refresh(existing_product)

    return existing_product


@router.delete('/admin/delete-product/{product_id}')

def delete_product(product_id: int, db: Session = Depends(get_db), current_user: dict = Depends(required_role('admin'))):

    existing_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()

    if not existing_product:
        raise HTTPException(status_code=404, detail='Product not found')

    inventory = db.query(InventoryModel).filter(InventoryModel.product_id == product_id).first()

    if inventory:
        db.delete(inventory)


    db.delete(existing_product)
    db.commit()

    return {'message': 'Product deleted successfully'}
    