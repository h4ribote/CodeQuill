import uuid
import zlib
from typing import List
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
import uvicorn
from bs4 import BeautifulSoup

import models, database

database.init_db()


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_root():
    return FileResponse('static/index.html')


@app.post("/api/articles/")
async def upload_article(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    if not file.filename.endswith('.html'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .html files are allowed.")

    contents = await file.read()
    
    soup = BeautifulSoup(contents, 'lxml')

    title_tag = soup.find('title')
    if not title_tag or not title_tag.string:
        raise HTTPException(status_code=400, detail="HTML file must have a <title> tag with content.")
    title = title_tag.string.strip()

    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
    if not meta_keywords or not meta_keywords.get('content'):
        raise HTTPException(status_code=400, detail="HTML file must have a <meta name=\"keywords\"> tag with content.")
    tags_str = meta_keywords.get('content', '').strip()

    compressed_content = zlib.compress(contents)

    new_article = models.Article(title=title, content=compressed_content)
    db.add(new_article)
    db.commit()
    db.refresh(new_article)

    tag_names = [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]
    for tag_name in tag_names:
        tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
        if not tag:
            tag = models.Tag(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        new_article.tags.append(tag)
    
    db.commit()
    
    return {"id": new_article.id.hex(), "title": new_article.title}


@app.get("/articles/{article_id}", response_class=HTMLResponse)
async def view_article_by_id(article_id: str, db: Session = Depends(database.get_db)):
    try:
        article_id_bytes = bytes.fromhex(article_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid article ID format")

    article = db.query(models.Article).options(joinedload(models.Article.tags)).filter(models.Article.id == article_id_bytes).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.view_count += 1
    
    for tag in article.tags:
        tag.view_count += 1
        
    db.commit()
    
    decompressed_content = zlib.decompress(article.content)
    return HTMLResponse(content=decompressed_content)


@app.get("/api/articles/{article_id}/related/")
async def get_related_articles(article_id: str, limit: int = 5, db: Session = Depends(database.get_db)):
    try:
        article_id_bytes = bytes.fromhex(article_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid article ID format")

    article = db.query(models.Article).options(joinedload(models.Article.tags)).filter(models.Article.id == article_id_bytes).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    tag_ids = [tag.id for tag in article.tags]
    if not tag_ids:
        return []

    related_articles = db.query(models.Article)\
        .join(models.article_tags)\
        .filter(models.article_tags.c.tag_id.in_(tag_ids))\
        .filter(models.Article.id != article_id_bytes)\
        .distinct()\
        .order_by(desc(models.Article.created_at))\
        .limit(limit)\
        .all()
    
    return [{"id": a.id.hex(), "title": a.title} for a in related_articles]


@app.get("/api/articles/search/")
async def search_articles(query: str, db: Session = Depends(database.get_db)):
    articles = db.query(models.Article).filter(
        (models.Article.title.ilike(f"%{query}%")) |
        (models.Article.tags.any(models.Tag.name.ilike(f"%{query}%")))
    ).all()
    
    return [{"id": a.id.hex(), "title": a.title} for a in articles]


@app.get("/api/articles/recommended/")
async def get_recommended_articles(limit: int = 5, db: Session = Depends(database.get_db)):
    top_tags = db.query(models.Tag).order_by(desc(models.Tag.view_count)).limit(limit).all()
    
    if not top_tags:
        return []

    top_tag_ids = [tag.id for tag in top_tags]
    recommended_articles = db.query(models.Article)\
        .join(models.article_tags)\
        .filter(models.article_tags.c.tag_id.in_(top_tag_ids))\
        .distinct()\
        .limit(limit)\
        .all()
        
    return [{"id": a.id.hex(), "title": a.title} for a in recommended_articles]


@app.get("/api/articles/random/")
async def get_random_articles(limit: int = 5, db: Session = Depends(database.get_db)):
    random_articles = db.query(models.Article).order_by(func.random()).limit(limit).all()
    return [{"id": a.id.hex(), "title": a.title} for a in random_articles]

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=28100)
