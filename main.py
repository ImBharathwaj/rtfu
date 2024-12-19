import asyncio
import time
import json
from random import randrange
from typing import Optional
from fastapi import FastAPI, Request, Response, status, HTTPException
from fastapi.params import Body, Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor
from database import engine, get_db
import models
import schemas
from sqlalchemy.orm import Session

# Creating an instance for application with FastAPI class
app = FastAPI()

# Binding database with engine and
models.Base.metadata.create_all(bind=engine)


while True:
    try:
        conn = psycopg2.connect(
            host="localhost", dbname="rtfu", user="postgres", password="root"
        )
        cursor = conn.cursor()
        print("Database connected succefully!")
        break
    except Exception as err:
        print(f"Error occurred while connecting database!")
        print(f"Error: {err}")
        time.sleep(2)


@app.get("/")
def read_root():
    return {"key": "value"}


@app.post("/createpost", status_code=status.HTTP_201_CREATED)
def createpost(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    return {"post": post.model_dump()}


@app.get("/posts")
def posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    print(type(post))
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with {id} was not found",
        )
    return post


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    print(type(post))
    if post.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with {id} does not exists",
        )
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(
    id: int, updated_post: schemas.PostUpdate, db: Session = Depends(get_db)
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with {id} does not exists",
        )

    post_query.update(updated_post.dict(), synchronize_session=False)

    db.commit()

    return post_query.first()
