import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
from app.src.db.database import get_db
from app.src.models.user import User as UserModel
from app.src.core.security import required_role
from app.src.schemas.products import ProductCreate, ProductUpdate, ProductResponse
from app.src.models.products import Product as ProductModel
from app.src.models.category import Category as CategoryModel
from app.src.models.inventory import Inventory as InventoryModel

router = APIRouter(tags=['Products'])

PRODUCT_IMAGES_PATH = "app/static/product_images"
os.makedirs(PRODUCT_IMAGES_PATH, exist_ok=True)

@router.get('/products', response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    products = db.query(ProductModel).all()
    if not products:
        return []
    return products


@router.post('/admin/add-product', response_model=ProductResponse)
def add_product(
    name: str = Form(...),
    description: str | None = Form(None),
    price: float = Form(...),
    category_id: int = Form(...),
    stock_quantity: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(required_role('admin'))
):
    # Check category 
    category_check = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if not category_check:
        raise HTTPException(status_code=400, detail='Category not found')

     # Check duplicate product
    existing_product = db.query(ProductModel).filter(ProductModel.name == name).first()
    if existing_product:
        raise HTTPException(status_code=400, detail='Product with this name already exists')


    # save image
    file_ext = image.filename.split('.')[-1]
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(PRODUCT_IMAGES_PATH, file_name)
    
    
    with open(file_path, 'wb') as f:
        f.write(image.file.read())
        
    
    image_path = f"/static/product_images/{file_name}"

    
    new_product = ProductModel(
        name=name,
        description=description,
        price=price,
        category_id=category_id,
        image_path = image_path
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    # Initialize Inventory
    new_inventory = InventoryModel(
        product_id=new_product.id,
        stock_quantity=stock_quantity
    )
    db.add(new_inventory)
    db.commit()

    return new_product



@router.put('/admin/update-product/{product_id}', response_model=ProductResponse)
def update_product(
    product_id: int,
    name: str | None = Form(None),
    description: str | None = Form(None),
    price: str | None = Form(None),
    category_id: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(required_role('admin'))
):
    # Fetch product
    existing_product = db.query(ProductModel).filter(
        ProductModel.id == product_id
    ).first()

    if not existing_product:
        raise HTTPException(status_code=404, detail='Product not found')

    # Validate category if provided
    if category_id is not None:
        category = db.query(CategoryModel).filter(
            CategoryModel.id == category_id
        ).first()

        if not category:
            raise HTTPException(status_code=400, detail="Invalid category_id")

    # Update simple fields
    if name is not None and name.strip() !="":
        existing_product.name = name

    if description is not None and description.strip() != "":
        existing_product.description = description

    if price is not None and price.strip() != "":
        existing_product.price = float(price)


    if category_id is not None and category_id.strip() != "":
        existing_product.category_id = category_id

    # Handle image update
    if image:
        filename = f"{uuid.uuid4()}_{image.filename}"
        file_path = os.path.join(PRODUCT_IMAGES_PATH, filename)

        with open(file_path, "wb") as f:
            f.write(image.file.read())

        existing_product.image_path = f"/static/product_images/{filename}"

    db.commit()
    db.refresh(existing_product)

    return existing_product




@router.delete('/admin/delete-product/{product_id}')
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(required_role('admin'))
):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')

    # Delete inventory
    inventory = db.query(InventoryModel).filter(
        InventoryModel.product_id == product_id
    ).first()

    if inventory:
        db.delete(inventory)

    # Delete image file from disk
    if product.image_path:
        # "/static/product_images/x.webp" → "app/static/product_images/x.webp"
        file_path = product.image_path.lstrip("/")
        file_path = os.path.join("app", file_path)

        if os.path.exists(file_path):
            os.remove(file_path)

    # Delete product
    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}
