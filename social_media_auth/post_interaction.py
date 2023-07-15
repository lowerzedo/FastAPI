from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
import uuid 

app = FastAPI()

# JWT Configuration
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    password: str

class PostIn(BaseModel):
    content: str

class Post(BaseModel):
    userid: str
    content: str
    id: str = str(uuid.uuid4())

class Like(BaseModel):
    liked: bool
    disliked: bool

fake_users_db = {
    "alice": {"username": "alice", "password": "alice123"},
    "bob": {"username": "bob", "password": "bob123"},
}

fake_posts_db = []
fake_likes_db = {}

def fake_hash_password(password: str):
    return "fakehashed" + password

class TokenData(BaseModel):
    username: str = None

class Token(BaseModel):
    access_token: str
    token_type: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not pwd_context.verify(hashed_password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/signup", response_model=Token)
async def signup_and_login_for_access_token(username: str, password: str):
    if fake_users_db.get(username):
        raise HTTPException(status_code=400, detail="Username exists")
    fake_users_db[username] = {"username": username, "password": fake_hash_password(password)}
    user = UserInDB(**fake_users_db[username])
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/post", response_model=List[Post])
async def read_posts():
    return fake_posts_db

@app.post("/post", response_model=Post)
async def submit_post(post: PostIn, token: str = Depends(oauth2_scheme)):
    try:
        username = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get('sub')
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    new_post = Post(userid=username, content=post.content)
    fake_posts_db.append(new_post)
    return new_post

@app.put("/post/{post_id}", response_model=Post)
async def update_post(post_id: int, post: PostIn, token: str = Depends(oauth2_scheme)):
    try:
        username = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get('sub')
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    for idx, existing_post in enumerate(fake_posts_db):
        if existing_post.id == post_id and existing_post.userid == username:
            fake_posts_db[idx] = Post(userid=username, content=post.content, id=post_id)
            return fake_posts_db[idx]
    raise HTTPException(status_code=404, detail="Post not found")

@app.post("/post/{post_id}/like", response_model=Like)
async def like_post(post_id: int, like: LikeIn, token: str = Depends(oauth2_scheme)):
    try:
        username = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get('sub')
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    for post in fake_posts_db:
        if post.id == post_id and post.userid != username:
            fake_likes_db[post_id] = like
            return like
    raise HTTPException(status_code=404, detail="Post not found or user not authorized")

