from typing import List

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_db
from src import manager as mng
from src.manager import get_current_user
from src.schemas import User, UserCreate, PostCreate, Post

router = APIRouter()


@router.post("/signup", response_model=User)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await mng.signup(user=user, db=db)


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    return await mng.login(form_data=form_data, db=db)


@router.post("/posts", response_model=Post)
async def create_post(post: PostCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await mng.create_post(post=post, current_user=current_user, db=db)


@router.get("/posts", response_model=List[Post])
async def get_posts(db: AsyncSession = Depends(get_db)):
    return await mng.get_posts(db=db)


@router.get("/posts/{post_id}", response_model=Post)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    return await mng.get_post(post_id=post_id, db=db)


@router.put("/posts/{post_id}", response_model=Post)
async def update_post(post_id: int, post: PostCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await mng.update_post(post_id=post_id, post=post, current_user=current_user, db=db)


@router.delete("/posts/{post_id}")
async def delete_post(post_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await mng.delete_post(post_id=post_id, current_user=current_user, db=db)


@router.post("/posts/{post_id}/like")
async def like_post(post_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await mng.like_post(post_id=post_id, current_user=current_user, db=db)


@router.post("/posts/{post_id}/dislike")
async def dislike_post(post_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await mng.dislike_post(post_id=post_id, current_user=current_user, db=db)


@router.get("/docs")
async def get_docs():
    return {"message": "API documentation"}