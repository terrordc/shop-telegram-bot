import asyncio
import typing
# Use an absolute import to get the database module from the src directory.
from src import database

# Forward declaration for type hinting. This does not cause imports.
if typing.TYPE_CHECKING:
    from src.models.categories import Category

class Item:
    def __init__(self, id: int) -> None:
        self.id = id

    async def __query(self, field: str) -> typing.Any:
        result = await database.fetch(f"SELECT {field} FROM items WHERE id = ?", (self.id,), fetchone=True)
        return result[0] if result else None

    async def __update(self, field: str, value: typing.Any) -> None:
        await database.execute(f"UPDATE items SET {field} = ? WHERE id = ?", (value, self.id), commit=True)

    @staticmethod
    def database_table() -> str:
        return """CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            composition TEXT,
            usage TEXT, 
            image_id TEXT,
            details_image_id TEXT,
            category_id INTEGER,
            price REAL NOT NULL,
            is_hidden INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL
        )"""

    @property
    async def name(self) -> str:
        return await self.__query("name")
    
    # ... other properties like description, composition, etc. ...
    
    @property
    async def category_id(self) -> int:
        return await self.__query("category_id")
    async def set_category_id(self, value: int) -> None:
        await self.__update("category_id", value)

    @property
    async def category(self) -> "Category":
        # LOCAL IMPORT: Solves the items <-> categories circular dependency.
        from src.models import categories
        cat_id = await self.category_id
        return categories.Category(cat_id) if cat_id else None

    @property
    async def price(self) -> float:
        return await self.__query("price")
    async def set_price(self, value: float) -> None:
        await self.__update("price", value)
    
    # ... other properties and methods like image_id, is_hidden, format_text, delete ...

### Module-level helper functions ###

# ... create() function ...

async def get_item_count_in_categories(category_ids: list[int]) -> int:
    if not category_ids:
        return 0
    placeholders = ', '.join('?' for _ in category_ids)
    query = f"SELECT COUNT(id) FROM items WHERE category_id IN ({placeholders})"
    result = await database.fetch(query, category_ids, fetchone=True)
    return result[0] if result else 0

async def delete_items_in_categories(category_ids: list[int]) -> int:
    if not category_ids:
        return 0
    
    count_to_delete = await get_item_count_in_categories(category_ids)

    if count_to_delete > 0:
        placeholders = ', '.join('?' for _ in category_ids)
        query = f"DELETE FROM items WHERE category_id IN ({placeholders})"
        await database.execute(query, category_ids, commit=True)
    
    return count_to_delete