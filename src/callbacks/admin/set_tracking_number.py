# src/callbacks/admin/set_tracking_number.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from states import AdminOrder # Import our new state group

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, state: FSMContext, message=None) -> None:
    order_id = data["oid"]

    # Store the order_id in the state's memory so we know which order to update
    await state.update_data(order_id=order_id)
    
    # Set the state to wait for the admin's next message
    await AdminOrder.waiting_for_tracking_number.set()

    # Ask the admin for the tracking number
    await callback_query.message.edit_text(constants.language.input_tracking_number)