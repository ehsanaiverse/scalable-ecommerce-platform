from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.src.db.database import get_db
from app.src.core.security import required_role
from app.src.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.src.models.category import Category as CategoryModel

router = APIRouter(tags=['Categories'])

@router.get('/categories', response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(CategoryModel).all()
    return categories

@router.post('/admin/categories', response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(required_role('admin'))
):
    existing_category = db.query(CategoryModel).filter(CategoryModel.name == category.name).first()
    if existing_category:
        raise HTTPException(status_code=400, detail='Category with this name already exists')
    
    new_category = CategoryModel(
        name=category.name,
        description=category.description
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.put('/admin/categories/{category_id}', response_model=CategoryResponse)
def update_category(
    category_id: int, 
    category: CategoryUpdate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(required_role('admin'))
):
    existing_category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if not existing_category:
        raise HTTPException(status_code=404, detail='Category not found')
    
    if category.name:
        # Check if name maps to another category
        name_check = db.query(CategoryModel).filter(CategoryModel.name == category.name).first()
        if name_check and name_check.id != category_id:
            raise HTTPException(status_code=400, detail='Category name already in use')
        existing_category.name = category.name
        
    if category.description is not None:
        existing_category.description = category.description
        
    db.commit()
    db.refresh(existing_category)
    return existing_category

@router.delete('/admin/categories/{category_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(required_role('admin'))
):
    existing_category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if not existing_category:
        raise HTTPException(status_code=404, detail='Category not found')
        
    # Check if category has products? (Optional but good practice, skipping for now to strict plan)
    
    db.delete(existing_category)
    db.commit()
    return None
