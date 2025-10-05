# models/reviews.py

from typing import Any
import database
from datetime import datetime
import constants

class Review:
    def __init__(self, id: int) -> None:
        self.id = id

    @property
    def database_table(self) -> str:
        """The SQL statement to create the reviews table."""
        return """CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            order_id INTEGER,
            review_text TEXT NOT NULL,
            rating INTEGER,
            created_at TEXT NOT NULL
        )"""

# This function will be called to save a new review
async def create(user_id: int, review_text: str, rating: int, order_id: int = None) -> None:
    """Creates a new review and saves it to the database."""
    current_time = datetime.now().strftime(constants.TIME_FORMAT)
    query = """
        INSERT INTO reviews (user_id, order_id, review_text, rating, created_at)
        VALUES (?, ?, ?, ?, ?)
    """
    await database.fetch(query, user_id, order_id, review_text, rating, current_time)