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
    


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message=None) -> None:
    user_orders = await models.orders.get_orders_by_user(user.id)

    # --- FIX #1: SMART RESPONSE LOGIC ---
    # Determine the correct object to respond with.
    target = message if message else callback_query.message
    
    if not user_orders:
        text = constants.language.no_orders_yet
        # If it's a message, answer. If it's a callback, edit.
        return await target.answer(text) if message else await target.edit_text(text)

    markup_list = []
    for order in user_orders:
        order_id = order.id
        date_created, status = await asyncio.gather(
            order.date_created_raw,
            order.status
        )
        
        date_str = date_created.split(" ")[0]
        status_text = get_status_text(status)
        button_text = f"Заказ #{order_id} от {date_str} - {status_text}"
        
        # The 'order_details' handler needs to know where to go back to.
        # Since 'profile' is gone, we'll remove the back button from the details page
        # by not providing an 'rd' (redirect) value.
        button_callback = f'{{"r":"user", "oid":{order_id}}}order_details'
        
        markup_list.append((button_text, button_callback))

    # --- FIX #2: REMOVE THE BROKEN "BACK" BUTTON ---
    # Since the user can use the main keyboard, a back button isn't strictly necessary here.
    # The old button pointed to 'profile', which no longer exists.
    # markup_list.append((constants.language.back, f"{constants.JSON_USER}profile"))

    final_markup = markups.create(markup_list)
    text = constants.language.your_orders

    # Use the smart response logic again
    if message:
        await target.answer(text=text, reply_markup=final_markup)
    else:
        # If coming from a callback, we can safely edit the message.
        await target.edit_text(text=text, reply_markup=final_markup)