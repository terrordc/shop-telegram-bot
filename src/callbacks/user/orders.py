# src/callbacks/user/orders.py

from aiogram import types
import asyncio
import models
import constants
from markups import markups
from aiogram.dispatcher import FSMContext

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

# The signature remains the same as it was. No changes to other files are needed.
async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    user_orders = await models.orders.get_orders_by_user(user.id)
    
    # --- Start of Simple Fix ---

    # If we were called by a text message from the main menu, `message` will exist.
    if message:
        # Handle the "no orders" case by sending a new message.
        if not user_orders:
            return await message.answer(constants.language.no_orders_yet)
    # If we were called by an inline button, `callback_query` will exist.
    else:
        # Handle the "no orders" case by editing the existing message.
        if not user_orders:
            # The 'profile' button doesn't exist, so let's just make a simple back button to the main menu
            # by not providing a destination. This will be handled by the dispatcher.
            return await callback_query.message.edit_text(
                text=constants.language.no_orders_yet,
                reply_markup=markups.create([(constants.language.back, f'{constants.JSON_USER}cancel')])
            )

    # This part to build the list of buttons is correct and doesn't change.
    markup = []
    for order in user_orders:
        order_id = order.id
        date_created, status = await asyncio.gather(
            order.date_created_raw,
            order.status
        )
        date_str = date_created.split(" ")[0]
        status_text = get_status_text(status)
        button_text = f"Заказ #{order_id} от {date_str} - {status_text}"
        button_callback = f'{{"r":"user", "oid":{order_id}}}order_details'
        markup.append((button_text, button_callback))
    
    # Let's add a back button that goes to the main menu.
    markup.append((constants.language.back, f'{constants.JSON_USER}cancel'))

    final_markup = markups.create(markup)
    text = constants.language.your_orders

    # Here is the simple logic to send the response.
    if message:
        await message.answer(text=text, reply_markup=final_markup)
    else:
        await callback_query.message.edit_text(
            text=text,
            reply_markup=final_markup
        )
    # --- End of Simple Fix ---