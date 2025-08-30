import json
import database
from typing import Any

import constants
import datetime

class Order:
    def __init__(self, id: int) -> None:
        self.id = id

    async def __query(self, field: str) -> Any:
        return (await database.fetch(f"SELECT {field} FROM orders WHERE id = ?", self.id))[0][0]

    async def __update(self, field: str, value: Any) -> None:
        await database.fetch(f"UPDATE orders SET {field} = ? WHERE id = ?", value, self.id)

    @property
    def database_table(self) -> str:
        return """CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            items TEXT NOT NULL,
            address TEXT,
            phone_number TEXT,
            email TEXT,
            full_name TEXT,
            comment TEXT,
            status INTEGER NOT NULL DEFAULT 0,
            date_created TEXT NOT NULL,
            date_updated TEXT,
            tracking_number TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )"""

    @property
    async def user_id(self) -> int:
        return await self.__query("user_id")
    @property
    async def full_name(self) -> str | None:
        return await self.__query("full_name")
    @property
    async def date_updated_raw(self) -> str | None:
        return await self.__query("date_updated")
    async def set_date_updated(self, value: str) -> None:
        await self.__update("date_updated", value)

    # items is a json string
        # items: [
        #   {
        #       "id": 1,
        #       "amount": 2
        #       "title": "title",
        #       "price": 100 # price per item
        #   }
        # ]
        # payment_method_id: 1
        # delivery_id: 1
        # delivery_price: 100

    @property
    async def __items_raw(self) -> str:
        return await self.__query("items")

    @property
    async def __items_json(self) -> dict:
        return json.loads(await self.__items_raw)

    @property
    async def items(self) -> list["__Item"]:
        return [self.__Item(item) for item in await self.__items_json]

    # in models/orders.py
    class __Item:
        # The constructor now correctly accepts a dictionary.
        def __init__(self, item_dict: dict) -> None:
            # We store the dictionary directly.
            self.dict = item_dict
        
        def __repr__(self) -> str:
            # For debugging, let's represent it as a string
            return json.dumps(self.dict)

        def __str__(self) -> str:
            return json.dumps(self.dict)

        # The 'id', 'amount', 'title', and 'price' properties now
        # access the stored dictionary directly, without json.loads.
        @property
        def id(self) -> int:
            return int(self.dict["id"])

        @property
        def amount(self) -> int:
            return int(self.dict["amount"])

        @property
        def title(self) -> str:
            return self.dict["title"]

        @property
        def price(self) -> float: # Prices can be floats, good practice
            return float(self.dict["price"])

    @property
    async def payment_method_id(self) -> int:
        return int((await self.__items_json)["payment_method_id"])

    @property
    async def delivery_id(self) -> int:
        return int((await self.__items_json)["delivery_id"])

    @property
    async def delivery_price(self) -> int:
        return int((await self.__items_json)["delivery_price"])

    @property
    async def address(self) -> str | None:
        return await self.__query("address")

    @property
    async def phone_number(self) -> str | None:
        return await self.__query("phone_number")

    @property
    async def email(self) -> str | None:
        return await self.__query("email")

    @property
    async def comment(self) -> str | None:
        return await self.__query("comment")

    @property
    async def status(self) -> int:
        return await self.__query("status")
    async def set_status(self, status: int) -> None:
        await self.__update("status", status)

    @property
    async def date_created_raw(self) -> str:
        return await self.__query("date_created")
    @property
    async def date_created(self) -> datetime.datetime:
        return datetime.datetime.strptime(await self.date_created_raw, constants.TIME_FORMAT)
    @property
    async def tracking_number(self) -> str | None:
        return await self.__query("tracking_number")
    async def set_tracking_number(self, value: str) -> None:
        await self.__update("tracking_number", value)

async def get_orders_by_status(status: int) -> list[Order]:
    """Fetches all orders with a given status, sorted by most recent first."""
    query = "SELECT id FROM orders WHERE status = ? ORDER BY id DESC"
    order_ids = await database.fetch(query, status)
    return [Order(order_id[0]) for order_id in order_ids]

async def get_orders_count_by_status(status: int) -> int:
    """Efficiently counts orders with a given status."""
    query = "SELECT COUNT(id) FROM orders WHERE status = ?"
    result = await database.fetch(query, status)
    return result[0][0] if result else 0

async def get_orders_by_user(user_id: int) -> list[Order]:
    """Fetches all orders for a given user, sorted by most recent first."""
    query = "SELECT id FROM orders WHERE user_id = ? ORDER BY id DESC"
    order_ids = await database.fetch(query, user_id)
    return [Order(order_id[0]) for order_id in order_ids]

def get_status_text(status_id: int) -> str:
    """Helper function to convert a status ID to human-readable text."""
    statuses = {
        0: constants.language.order_status_new,
        1: constants.language.order_status_processing,
        2: constants.language.order_status_shipped,
        3: constants.language.order_status_delivered,
        4: constants.language.order_status_cancelled,
        5: constants.language.order_status_cancellation_requested, # <-- ADD THIS
        6: constants.language.order_status_pending_payment, # <-- ADD THIS LINE
    }
    return statuses.get(status_id, constants.language.order_status_unknown)

# In models/orders.py
# REPLACE your old create function with this one

async def create(
    user_id: int,
    items_json: str,
    date_created: str,
    full_name: str | None = None,
    address: str | None = None,
    phone_number: str | None = None,
    email: str | None = None,
    comment: str | None = None,
    status: int = 0  # <-- ADD status as an argument with a default of 0
) -> Order:
    # Add 'status' to the query
    query = "INSERT INTO orders (user_id, items, date_created, full_name, address, phone_number, email, comment, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    # Add status to the parameters tuple
    params = (user_id, items_json, date_created, full_name, address, phone_number, email, comment, status)
    await database.fetch(query, *params)
    return Order((await database.fetch("SELECT id FROM orders ORDER BY id DESC LIMIT 1"))[0][0])


