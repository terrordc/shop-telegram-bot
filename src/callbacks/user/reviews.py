# callbacks/user/reviews.py

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
            order_line = f"Заказ /{order_id} - {item_name} от {date_created}"
            orders_text_list.append(f"<code>{order_line}</code>")
    
    orders_text = "\n".join(orders_text_list)
    
    # --- START OF FIX ---
    # This now uses the simple, corrected footer from your language file.
    
    if not user_orders:
        # This case is for when a user has no orders. We can't build a list.
        final_text = (
            f"У вас еще нет заказов для отзыва.\n"
            f"{constants.language.review_footer}"
        )
    else:
        # This is the main text block, now using the corrected footer.
        final_text = (
            f"❗️ Если вы хотите оставить отзыв о конкретном заказе или товаре - просто в ответном сообщении отправьте цифрами номер этого заказа\n"
            f"➖➖\n"
            f"🍕 Список Ваших заказов:\n"
            f"➖➖\n"
            f"{orders_text}\n"
            f"{constants.language.review_footer}" # Use the corrected footer here
        )
    # --- END OF FIX ---

    await LeaveReview.waiting_for_input.set()
    await message.answer(final_text, parse_mode="HTML", disable_web_page_preview=True)