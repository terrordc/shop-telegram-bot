# src/callbacks/states/AdminOrder_waiting_for_tracking_number.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from aiogram.utils.exceptions import TelegramAPIError

# Status ID for "Shipped"
SHIPPED_STATUS = 2

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    tracking_number = message.text
    state_data = await state.get_data()
    order_id = state_data.get("order_id")

    if not order_id:
        # Failsafe if something went wrong
        await state.finish()
        return await message.answer("Произошла ошибка, попробуйте снова.")

    # 1. Get the order object and update it
    order = models.orders.Order(order_id)
    await order.set_tracking_number(tracking_number)
    await order.set_status(SHIPPED_STATUS)

    # 2. Finish the FSM state
    await state.finish()
    
    # 3. Notify the admin of success
    await message.answer(
        constants.language.order_marked_as_shipped_admin.format(
            order_id=order_id,
            tracking_number=tracking_number
        )
    )

    # 4. Notify the user that their order has been shipped
    try:
        order_user_id = await order.user_id
        await message.bot.send_message(
            chat_id=order_user_id,
            text=constants.language.user_notification_shipped.format(
                order_id=order_id,
                tracking_number=tracking_number
            ),
            parse_mode="HTML"
        )
    except TelegramAPIError as e:
        # Handle cases where the user has blocked the bot
        print(f"Failed to send shipping notification to user {order_user_id}: {e}")
        await message.answer(f"⚠️ Не удалось отправить уведомление пользователю (ID: {order_user_id}). Возможно, он заблокировал бота.")