from aiogram import types
from aiogram.dispatcher import FSMContext
import asyncio
import models
import constants
from states import LeaveReview

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    
    user_orders = await models.orders.get_orders_by_user(user.id)
    
    orders_text_list = []
    if user_orders:
        for order in user_orders:
            order_id = order.id
            date_created, items = await asyncio.gather(
                order.date_created,
                order.items
            )
            item_name = items[0].title if items else "Товар"
            
            # --- START OF FIX ---
            # Format the order ID as a plain-text command. Telegram will make this blue.
            orders_text_list.append(f"Заказ /{order_id} - {item_name} от {date_created}")
            # --- END OF FIX ---
    
    orders_text = "\n".join(orders_text_list)
    
    if not user_orders:
        final_text = f"{constants.language.no_orders_for_review}\n\n{constants.language.review_footer}"
    else:
        final_text = f"{constants.language.review_header}\n{orders_text}\n{constants.language.review_footer}"

    await LeaveReview.waiting_for_input.set()
    
    # --- CRITICAL CHANGE: REMOVE parse_mode="HTML" ---
    # Send the message as plain text.
    await message.answer(final_text)