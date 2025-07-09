import typing
# Use an absolute import to get the database module from the src directory.
from src import database

# Forward declaration for type hinting. This does not cause imports.
if typing.TYPE_CHECKING:
    from src.models import items
    from src.models.items import Item

class Category:
    def __init__(self, id: int) -> None:
        self.id = id

    async def __query(self, field: str) -> typing.Any:
    # We pass the tuple directly now, no unpacking
        result = await database.fetch(f"SELECT {field} FROM categories WHERE id = ?", (self.id,), fetchone=True)
        return result[0] if result else None

    async def __update(self, field: str, value: typing.Any) -> None:
        await database.execute(f"UPDATE categories SET {field} = ? WHERE id = ?", (value, self.id), commit=True)

    @staticmethod
    def database_table() -> str:
        return """CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            parent_id INTEGER,
            is_hidden INTEGER,
            FOREIGN KEY (parent_id) REFERENCES categories (id)
        )"""

    @property
    async def name(self) -> str:
        return await self.__query("name")
    async def set_name(self, value: str) -> None:
        await self.__update("name", value)

    # ... other properties ...
    
    @property
    async def children(self) -> list["Category"]:
        results = await database.fetch("SELECT id FROM categories WHERE parent_id = ?", (self.id,))
        return [Category(row[0]) for row in results]
    
    # ... other properties and methods ...

    async def get_all_descendants(self) -> list['Category']:
        all_descendants = []
        queue = [self]
        head = 0
        while head < len(queue):
            current_category = queue[head]
            head += 1
            direct_children = await current_category.children
            for child in direct_children:
                all_descendants.append(child)
                queue.append(child)
        return all_descendants

    async def cascade_delete(self) -> tuple[int, int]:
        from src.models import items

        descendants = await self.get_all_descendants()
        all_category_ids = [self.id] + [c.id for c in descendants]
        deleted_item_count = await items.delete_items_in_categories(all_category_ids)
        
        if all_category_ids:
            placeholders = ', '.join('?' for _ in all_category_ids)
            query = f"DELETE FROM categories WHERE id IN ({placeholders})"
            await database.execute(query, all_category_ids, commit=True)
        
        deleted_category_count = len(all_category_ids)
        return deleted_category_count, deleted_item_count
        
    async def delete(self) -> None:
        await database.execute("DELETE FROM categories WHERE id = ?", (self.id,), commit=True)

### Module-level helper functions ###

async def get_categories(parent_id: int | None = None) -> list[Category]:
    if parent_id is not None:
        query = "SELECT id FROM categories WHERE parent_id=?"
        params = (parent_id,)
    else:
        query = "SELECT id FROM categories"
        params = ()
    
    # You can leave this print statement in for now to be 100% sure
    print(f"DEBUG: Executing get_categories. QUERY='{query}', PARAMS={params}")

    results = await database.fetch(query, params)
    return [Category(row['id']) for row in results] # <-- Use row['id'] now!

async def create(name: str, parent_id: int = 0) -> Category:
    cursor = await database.execute("INSERT INTO categories (name, parent_id, is_hidden) VALUES (?, ?, 0)", (name, parent_id), commit=True)
    return Category(cursor.lastrowid)