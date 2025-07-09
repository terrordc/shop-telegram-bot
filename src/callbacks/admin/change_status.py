# Create this new file: src/callbacks/admin/change_status.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import datetime # <--- ADD THIS LINE
import constants # <--- MAKE SURE THIS IS HERE TOO
async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    order_id = data["oid"]
    new_status = data["st"]
    order = models.orders.Order(order_id)

    # Set the new status
    await order.set_status(new_status)
    await order.set_date_updated(datetime.datetime.now().strftime(constants.TIME_FORMAT))

    await callback_query.answer(f"Статус заказа #{order_id} изменен.")


    # TODO: Optionally, notify the user about the status change.
    # order_user_id = await order.user_id
    # await bot.send_message(order_user_id, f"Статус вашего заказа #{order_id} был изменен.")

    # Refresh the details view to show the updated status
    from . import order_details
    await order_details.execute(callback_query, user, data)