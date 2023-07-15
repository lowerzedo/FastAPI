from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "user_detail"

    id = Column(Integer, primary_key=True, index=True)
    username =  Column(String, unique=True, index=True)
    fullname =  Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    diabled = Column(Boolean, default=False)

    items = relationship("Post", back_populates="owner")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("user_detail.id"))

    owner = relationship("User", back_populates="posts")
