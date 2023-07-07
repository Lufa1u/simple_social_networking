from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    email: str


class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


class PostCreate(BaseModel):
    title: str
    content: str


class Post(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    likes: int

    class Config:
        orm_mode = True
