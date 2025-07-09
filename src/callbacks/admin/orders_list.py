# src/callbacks/admin/orders_list.py

from aiogram import types
import asyncio
import models
import constants
from markups import markups

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    status_id = data["s"]

    orders_list = await models.orders.get_orders_by_status(status_id)

    if not orders_list:
        return await callback_query.message.edit_text(
            text="В этой категории нет заказов.",
            reply_markup=markups.create([
                (constants.language.back, f'{constants.JSON_ADMIN}orders')
            ])
        )

    markup = []
    for order in orders_list:
        # --- THE FIX IS HERE ---
        # Get the simple, non-awaitable value first.
        order_id = order.id
        
        # Now, gather only the coroutines.
        user_id, date_created_raw = await asyncio.gather(
            order.user_id,
            order.date_created_raw
        )
        
        order_user = models.users.User(user_id)
        username = await order_user.username or f"ID: {user_id}"

        date_str = date_created_raw.split(" ")[0]
        button_text = f"Заказ #{order_id} от {username} ({date_str})"
        
        button_callback = f'{{"r":"admin", "oid":{order_id}, "s":{status_id}}}order_details'
        markup.append((button_text, button_callback))

    markup.append((constants.language.back, f'{constants.JSON_ADMIN}orders'))

    await callback_query.message.edit_text(
        text=f"Список заказов (статус: {status_id})",
        reply_markup=markups.create(markup)
    )