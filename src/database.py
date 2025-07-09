import aiosqlite

async def execute(query: str, args: tuple = (), commit: bool = False) -> aiosqlite.Cursor:
    """
    Executes a query (e.g., INSERT, UPDATE, DELETE).
    Use for actions that don't need to return data.
    """
    async with aiosqlite.connect("database.db") as db:
        cursor = await db.execute(query, args)
        if commit:
            await db.commit()
        return cursor

async def fetch(query: str, args: tuple = (), fetchone: bool = False) -> list | aiosqlite.Row | None:
    """
    Fetches data from the database (SELECT).
    - fetchone=True: Returns a single row or None.
    - fetchone=False (default): Returns a list of all rows.
    """
    async with aiosqlite.connect("database.db") as db:
        # Enable row factory to access columns by name (e.g., row['id'])
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(query, args)
        
        if fetchone:
            return await cursor.fetchone()
        else:
            return await cursor.fetchall()