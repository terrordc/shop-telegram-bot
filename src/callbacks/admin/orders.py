# Create this new file: src/callbacks/admin/orders.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import asyncio
import models
import constants
from markups import markups

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    # We can count how many orders are in each status to make the buttons more informative
    new_orders_count, cancellation_requests_count = await asyncio.gather(
        models.orders.get_orders_count_by_status(0), # Status 0 for "New"
        models.orders.get_orders_count_by_status(5)  # Status 5 for "Cancellation Requested"
    )

    # Status 0 = New, 5 = Cancellation Requested
    # We will build buttons that pass the status ID to the next handler.
    new_orders_callback = f'{{"r":"admin", "s":0}}orders_list'
    cancellation_callback = f'{{"r":"admin", "s":5}}orders_list'

    markup = markups.create([
        # Button shows the count and leads to the list view for that status
        (f"({new_orders_count}){constants.language.filter_new_orders}", new_orders_callback),
        (f"({cancellation_requests_count}){constants.language.filter_cancellation_requests}", cancellation_callback),
        (constants.language.back, f'{constants.JSON_ADMIN}adminPanel')
    ])

    await callback_query.message.edit_text(
        text=constants.language.admin_orders_menu_title,
        reply_markup=markup
    )