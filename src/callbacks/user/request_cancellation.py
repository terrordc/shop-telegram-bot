# src/callbacks/user/request_cancellation.py
from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants

# Define the new status ID
CANCELLATION_REQUESTED_STATUS = 5

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    order_id = data["oid"]
    order = models.orders.Order(order_id)

    current_status = await order.status

    if current_status != 0:
        await callback_query.answer(constants.language.cancellation_not_possible, show_alert=True)
        return

    # Update the order status to our new "Cancellation Requested" state
    await order.set_status(CANCELLATION_REQUESTED_STATUS)
    
    # Acknowledge the action with an alert
    await callback_query.answer(
        constants.language.cancellation_requested_success.format(order_id=order_id),
        show_alert=True
    )

    # Now, simply edit the message to confirm, and remove the buttons
    await callback_query.message.edit_text(
        text=f"✅ Запрос на отмену заказа #{order_id} отправлен."
    )