# src/callbacks/user/orders.py

from aiogram import types
import asyncio
import models
import constants
from markups import markups

# in src/callbacks/user/orders.py

def get_status_text(status_id: int) -> str:
    """Helper function to convert a status ID to human-readable text."""
    statuses = {
        0: constants.language.order_status_new,
        1: constants.language.order_status_processing,
        2: constants.language.order_status_shipped,
        3: constants.language.order_status_delivered,
        4: constants.language.order_status_cancelled,
        5: constants.language.order_status_cancellation_requested,
    }
    return statuses.get(status_id, constants.language.order_status_unknown)
    


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    user_orders = await models.orders.get_orders_by_user(user.id)

    if not user_orders:
        return await callback_query.message.edit_text(
            text=constants.language.no_orders_yet,
            reply_markup=markups.create([
                (constants.language.back, f"{constants.JSON_USER}profile")
            ])
        )

    markup = []
    for order in user_orders:
        # --- THE FIX IS HERE ---
        # Get the simple value first, no await needed.
        order_id = order.id
        
        # Now, gather only the things that need to be awaited.
        date_created, status = await asyncio.gather(
            order.date_created_raw,
            order.status
        )
        
        date_str = date_created.split(" ")[0]
        status_text = get_status_text(status)
        button_text = f"Заказ #{order_id} от {date_str} - {status_text}"
        
        button_callback = f'{{"r":"user", "oid":{order_id}}}order_details'
        
        markup.append((button_text, button_callback))

    markup.append((constants.language.back, f"{constants.JSON_USER}profile"))

    await callback_query.message.edit_text(
        text=constants.language.your_orders,
        reply_markup=markups.create(markup)
    )