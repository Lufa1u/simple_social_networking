from datetime import timedelta

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import PyJWTError, decode
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from config import get_db, AuthConfig
from src.auth import pwd_context, create_access_token
from src.models import UserModel, PostModel, LikeModel
from src.schemas import UserCreate, PostCreate, User, Post


async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(OAuth2PasswordBearer(tokenUrl="social/login"))):
    try:
        payload = decode(token, AuthConfig.SECRET_KEY, algorithms=[AuthConfig.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user = await db.execute(select(UserModel).where(UserModel.username == username))
    return user.scalar_one_or_none()


async def check_like_exists(user_id: int, post_id: int, db: AsyncSession):
    return await db.scalar(select(LikeModel).where(LikeModel.user_id == user_id, LikeModel.post_id == post_id))


async def signup(user: UserCreate, db: AsyncSession):
    rows = (await db.execute(select(UserModel.username, UserModel.email).select_from(UserModel))).all()
    all_usernames = [usernames for usernames, _ in rows]
    all_emails = [emails for _, emails in rows]
    if user.username in all_usernames or user.email in all_emails:
        raise HTTPException(status_code=409, detail="User already exist")
    new_user = UserModel(username=user.username, password_hash=pwd_context.hash(user.password), email=user.email)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def login(form_data: OAuth2PasswordRequestForm, db: AsyncSession):
    user = (await db.execute(select(UserModel).where(UserModel.username == form_data.username))).scalar_one_or_none()
    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


async def create_post(post: PostCreate, current_user: User, db: AsyncSession):
    new_post = PostModel(title=post.title, content=post.content, user_id=current_user.id)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return Post(**new_post.__dict__, likes=0)


async def get_posts(db: AsyncSession):
    subquery = select(LikeModel.post_id, func.count().label("total_likes")).group_by(LikeModel.post_id).subquery()
    posts = (await db.execute(
        select(PostModel.id, PostModel.title, PostModel.content, PostModel.user_id, subquery.c.total_likes).
        outerjoin(subquery, PostModel.id == subquery.c.post_id))).fetchall()
    result = []
    for post in posts:
        result.append(Post(id=post.id, user_id=post.user_id, title=post.title,
                           content=post.content, likes=post.total_likes if post.total_likes else 0))
    return result


async def get_post(post_id: int, db: AsyncSession):
    subquery = select(LikeModel.post_id, func.count().label("total_likes")).where(LikeModel.post_id == post_id).group_by(LikeModel.post_id).subquery()
    post = (await db.execute(
        select(PostModel.id, PostModel.title, PostModel.content, PostModel.user_id, subquery.c.total_likes).
        where(PostModel.id == post_id).outerjoin(subquery, PostModel.id == post_id))).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return Post(id=post.id, user_id=post.user_id, title=post.title,
                content=post.content, likes=post.total_likes if post.total_likes else 0)


async def update_post(post_id: int, post: PostCreate, current_user: User, db: AsyncSession):
    existing_post = (await db.execute(select(PostModel).where(PostModel.id == post_id))).scalar_one_or_none()
    if not existing_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if existing_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    existing_post.title = post.title
    existing_post.content = post.content
    await db.commit()
    await db.refresh(existing_post)
    return existing_post


async def delete_post(post_id: int, current_user: User, db: AsyncSession):
    post = (await db.execute(select(PostModel).where(PostModel.id == post_id))).scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    await db.delete(post)
    await db.commit()
    return {"message": "Post deleted successfully"}


async def like_post(post_id: int, current_user: User, db: AsyncSession):
    post = (await db.execute(select(PostModel).where(PostModel.id == post_id))).scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post notfound")
    if post.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot like your own post")
    like = await check_like_exists(post_id=post_id, user_id=current_user.id, db=db)
    if like:
        raise HTTPException(status_code=409, detail="You already liked this post")
    new_like = LikeModel(user_id=current_user.id, post_id=post_id)
    db.add(new_like)
    await db.commit()
    return {"message": "Post liked successfully"}


async def dislike_post(post_id: int, current_user: User, db: AsyncSession):
    post = (await db.execute(select(PostModel).where(PostModel.id == post_id))).scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot dislike your own post")
    like = await check_like_exists(post_id=post_id, user_id=current_user.id, db=db)
    if not like:
        raise HTTPException(status_code=409, detail="Not worth a like")
    await db.delete(like)
    await db.commit()
    return {"message": "Post disliked successfully"}
