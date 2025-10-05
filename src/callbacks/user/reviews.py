# callbacks/user/reviews.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import asyncio
import models
import constants
from states import LeaveReview

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    
    # 1. Get all orders for the user
    user_orders = await models.orders.get_orders_by_user(user.id)
    
    # 2. Build the list of orders text
    orders_text_list = []
    if user_orders:
        for order in user_orders:
            order_id, date_created, items = await asyncio.gather(
                order.id,
                order.date_created,
                order.items
            )
            # Just show the name of the first item for simplicity
            item_name = items[0].title if items else "Товар"
            orders_text_list.append(f"Заказ {order_id} - {item_name} от {date_created}")
    
    orders_text = "\n".join(orders_text_list)
    
    # 3. Construct the final message
    if not user_orders:
        final_text = f"{constants.language.no_orders_for_review}\n\n{constants.language.review_footer}"
    else:
        final_text = f"{constants.language.review_header}\n{orders_text}\n{constants.language.review_footer}"

    # 4. Set the state and send the message
    await LeaveReview.waiting_for_input.set()
    await message.answer(final_text)