import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from sqlite3 import Error


app = FastAPI()

DATABASE = "data-subtitle-indonesia.db"

class Item(BaseModel):
    title: str
    description: str
    imdb_id: str
    cover_url: str
    magnet_url: str
    is_uploaded: bool
    video_id: str
    trailer_id: str
    filename: str
    owner: str

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
    except Error as e:
        print(e)
    return conn

def init_db():
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                imdb_id TEXT NOT NULL,
                cover_url TEXT NOT NULL,
                magnet_url TEXT NOT NULL,
                is_uploaded BOOLEAN NOT NULL,
                video_id TEXT NOT NULL,
                trailer_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                owner TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/items/")
async def create_item(item: Item):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        
        # Retry mechanism
        print(item)
        for attempt in range(5):
            try:
                cursor.execute('SELECT * FROM items WHERE filename = ?', (item.filename,))
                existing_item = cursor.fetchone()

                if existing_item:
                    raise HTTPException(status_code=400, detail="Item exists.")

                cursor.execute('''
                    INSERT INTO items (title, description, imdb_id, cover_url, magnet_url, is_uploaded, video_id, trailer_id, filename, owner)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (item.title, item.description, item.imdb_id, item.cover_url, item.magnet_url, item.is_uploaded, item.video_id, item.trailer_id, item.filename, item.owner))
                conn.commit()
                conn.close()
                return {"id": cursor.lastrowid, **item.model_dump()}
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < 4:  # if the database is locked, retry
                    time.sleep(0.1)  # wait a little before retrying
                    conn = create_connection()  # Recreate the connection
                    cursor = conn.cursor()
                else:
                    print (e)
                    raise HTTPException(status_code=500, detail="Database connection error or locked")
    else:
        raise HTTPException(status_code=500, detail="Database connection error")

@app.put("/items/{filename}")
async def update_item(filename: str, item: Item):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()

        # Retry mechanism
        for attempt in range(5):
            try:
                cursor.execute('SELECT * FROM items WHERE filename = ?', (filename,))
                existing_item = cursor.fetchone()

                if not existing_item:
                    raise HTTPException(status_code=404, detail="Item not found.")

                cursor.execute('''UPDATE items SET title = ?, description = ?, cover_url = ?, magnet_url = ?, is_uploaded = ?, video_id = ?, trailer_id = ?, owner = ? WHERE filename = ? AND owner = ?''', (item.title, item.description, item.cover_url, item.magnet_url, item.is_uploaded, item.video_id, item.trailer_id, filename, item.owner))
                conn.commit()
                conn.close()
                return {"message": "Item updated successfully."}
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < 4:
                    time.sleep(0.1)
                    conn = create_connection()
                    cursor = conn.cursor()
                else:
                    raise HTTPException(status_code=500, detail="Database connection error or locked")
    else:
        raise HTTPException(status_code=500, detail="Database connection error")

# GET disini
@app.get("/items/{filename}")
async def read_item_by_filename(filename: str):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM items WHERE filename = ?', (filename,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "imdb_id": row[3],
                "cover_url": row[4],
                "magnet_url": row[5],
                "is_uploaded": row[6],
                "video_id": row[7],
                "trailer_id": row[8],
                "filename": row[9],
                "owner": row[10]
            }
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    else:
        raise HTTPException(status_code=500, detail="Database connection error")

@app.get("/items/{id}")
async def read_item_by_id(id: int):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM items WHERE id = ?', (id,))
            row = cursor.fetchone()
            conn.close()  # Close the connection after fetching

            if row:
                return {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "imdb_id": row[3],
                    "cover_url": row[4],
                    "magnet_url": row[5],
                    "is_uploaded": row[6],
                    "video_id": row[7],
                    "trailer_id": row[8],
                    "filename": row[9],
                    "owner": row[10]
                }
            else:
                raise HTTPException(status_code=404, detail="Item not found")
        except sqlite3.Error as e:  # Catch sqlite3 errors specifically
            conn.close() # Ensure connection is closed even on error
            raise HTTPException(status_code=500, detail=f"Database error: {e}")
    else:
        raise HTTPException(status_code=500, detail="Database connection error")

@app.get("/items/{imdb_id}")
async def read_item_by_imdb_id(imdb_id: str):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM items WHERE imdb_id = ?', (imdb_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "imdb_id": row[3],
                "cover_url": row[4],
                "magnet_url": row[5],
                "is_uploaded": row[6],
                "video_id": row[7],
                "trailer_id": row[8],
                "filename": row[9],
                "owner": row[10]
            }
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    else:
        raise HTTPException(status_code=500, detail="Database connection error")
    
@app.get("/items/{description}")
async def read_items_by_description(description: str):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM items WHERE description = ?', (description,))
        rows = cursor.fetchall()
        conn.close()

        if rows:
            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "imdb_id": row[3],
                    "cover_url": row[4],
                    "magnet_url": row[5],
                    "is_uploaded": row[6],
                    "video_id": row[7],
                    "trailer_id": row[8],
                    "filename": row[9],
                    "owner": row[10]
                }
                for row in rows
            ]
        else:
            raise HTTPException(status_code=404, detail="No items found with the specified description.")
    else:
        raise HTTPException(status_code=500, detail="Database connection error")

@app.get("/items/sub/uploaded")
async def read_items_if_uploaded():
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM items WHERE is_uploaded = ?', (True,))
        rows = cursor.fetchall()
        conn.close()

        if rows:
            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "imdb_id": row[3],
                    "cover_url": row[4],
                    "magnet_url": row[5],
                    "is_uploaded": row[6],
                    "video_id": row[7],
                    "trailer_id": row[8],
                    "filename": row[9],
                    "owner": row[10]
                }
                for row in rows
            ]
        else:
            raise HTTPException(status_code=404, detail="No items found.")
    else:
        raise HTTPException(status_code=500, detail="Database connection error")

@app.get("/items/sub/search")
async def search_items_subquery(substring: str):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        # Update the query to filter by is_uploaded = true
        cursor.execute("SELECT * FROM items WHERE title LIKE ? AND is_uploaded = ?", (f"%{substring}%", True))
        rows = cursor.fetchall()
        conn.close()

        if rows:
            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "imdb_id": row[3],
                    "cover_url": row[4],
                    "magnet_url": row[5],
                    "is_uploaded": row[6],
                    "video_id": row[7],
                    "trailer_id": row[8],
                    "filename": row[9],
                    "owner": row[10]
                }
                for row in rows
            ]
        else:
            raise HTTPException(status_code=404, detail="No items found.")
    else:
        raise HTTPException(status_code=500, detail="Database connection error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)