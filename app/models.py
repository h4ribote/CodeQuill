# models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# Association table for the many-to-many relationship between articles and tags
article_tags = Table('article_tags', Base.metadata,
    Column('article_id', Integer, ForeignKey('articles.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    file_path = Column(String, unique=True)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tags = relationship("Tag", secondary=article_tags, back_populates="articles")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    view_count = Column(Integer, default=0)

    articles = relationship("Article", secondary=article_tags, back_populates="tags")
