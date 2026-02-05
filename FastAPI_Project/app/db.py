# ORM - Object relational Mapping
from collections.abc import AsyncGenerator
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from fastapi import Depends

DATABASE_URL="sqlite+aiosqlite:///./test.db"

class Base(DeclarativeBase):
    pass

# set up a one-to-many relationship
class User(SQLAlchemyBaseUserTableUUID, Base):
    posts = relationship("Post", back_populates="user")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) # every post has a unique random ID
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False) # allows link to know the users id
    caption = Column(Text)
    url = Column(String, nullable=False)  # cant be null
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="posts")
    
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

# Creates database and tables
async def create_db_and_tables():
    async with engine.begin() as conn:
        # Finds all the classes that inhertit from declarative base and create them inside of the database
        await conn.run_sync(Base.metadata.create_all)
        
# Get a session to access database allowing read and write asyncronously
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
        
# Gets user database table
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)