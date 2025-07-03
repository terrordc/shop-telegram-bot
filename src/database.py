# src/database.py

import aiosqlite

async def fetch(query: str, *args) -> list:
    # Use the 'async with' block to ensure the connection is closed
    async with aiosqlite.connect("database.db") as db:
        
        # --- THIS IS THE KEY ---
        # Set the row_factory to return dictionary-like rows
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(query, args)
        # Note: You don't need db.commit() for a SELECT statement, only for INSERT/UPDATE/DELETE
        # await db.commit() 
        
        return list(await cursor.fetchall())