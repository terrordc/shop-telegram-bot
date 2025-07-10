# src/models/items.py

import json
from typing import Any
import database
import asyncio

class Item:
    def __init__(self, id: int) -> None:
        self.id = id

    async def __query(self, field: str) -> Any:
        # This is fine, no changes needed
        return (await database.fetch(f"SELECT {field} FROM items WHERE id = ?", self.id))[0][0]

    async def __update(self, field: str, value: Any) -> None:
        # This is fine, no changes needed
        await database.fetch(f"UPDATE items SET {field} = ? WHERE id = ?", value, self.id)

    @property
    def database_table(self) -> str:
        # --- FIX ---
        # Removed the trailing comma after 'is_hidden INTEGER'
        return """CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            composition TEXT,
            usage TEXT,
            image_id TEXT,
            details_image_id TEXT,
            price REAL NOT NULL,
            is_hidden INTEGER
        )"""

    # ... all the property getters and setters are fine ...
    @property
    async def name(self) -> str:
        return await self.__query("name")
    async def set_name(self, value: str) -> None:
        await self.__update("name", value)

    @property
    async def description(self) -> str:
        return await self.__query("description")
    async def set_description(self, value: str) -> None:
        await self.__update("description", value)
    @property
    async def composition(self) -> str | None:
        return await self.__query("composition")
    async def set_composition(self, value: str) -> None:
        await self.__update("composition", value)

    @property
    async def details_image_id(self) -> str | None:
        return await self.__query("details_image_id")
    async def set_details_image_id(self, value: str) -> None:
        await self.__update("details_image_id", value)

    @property
    async def usage(self) -> str | None:
        return await self.__query("usage")
    async def set_usage(self, value: str) -> None:
        await self.__update("usage", value)

    @property
    async def price(self) -> float:
        return await self.__query("price")
    async def set_price(self, value: float) -> None:
        await self.__update("price", value)

    @property
    async def image_id(self) -> str:
        return await self.__query("image_id")
    async def set_image_id(self, value: str) -> None:
        await self.__update("image_id", value)

    @property
    async def is_hidden(self) -> bool:
        return bool(await self.__query("is_hidden"))
    async def set_is_hidden(self, value: bool) -> None:
        await self.__update("is_hidden", int(value))

    async def format_text(self, template: str, currency: str) -> str:
        # This is fine, no changes needed
        name, description, price, = await asyncio.gather(
            self.name,
            self.description,
            self.price,
        )
        return template.replace("%n", name).replace("%d", description).replace("%p", f"{price} {currency}")

    async def delete(self) -> None:
        # This is fine, no changes needed
        await database.fetch("DELETE FROM items WHERE id = ?", self.id)

async def create(
    name: str,
    description: str,
    price: float,
    image_id: str
) -> Item:
    # --- FIX ---
    # Made the INSERT query robust by specifying column names.
    # This prevents errors if the table schema changes in the future.
    # It also correctly handles columns that are not set on creation (like 'composition').
    query = """
        INSERT INTO items (name, description, price, image_id, is_hidden)
        VALUES (?, ?, ?, ?, ?)
    """
    await database.fetch(query, name, description, price, image_id, 0)
    # This logic to get the last created ID is fine
    return Item((await database.fetch("SELECT id FROM items ORDER BY id DESC LIMIT 1"))[0][0])

async def get_all_visible_items() -> list[Item]:
    # This is fine, no changes needed
    """Fetches all items that are not hidden, sorted by ID."""
    query = "SELECT id FROM items WHERE is_hidden = 0 ORDER BY id"
    item_ids = await database.fetch(query)
    return [Item(item_id[0]) for item_id in item_ids]
async def get_all_items() -> list[Item]:
    """Fetches all items, including hidden ones, sorted by ID."""
    query = "SELECT id FROM items ORDER BY id"
    item_ids = await database.fetch(query)
    return [Item(item_id[0]) for item_id in item_ids]