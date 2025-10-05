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
            
            # --- START OF FIX ---
            # Format the entire line inside a <code> tag for clean, monospaced formatting.
            # Only the /<order_id> part will be blue and clickable.
            order_line = f"Заказ /{order_id} - {item_name} от {date_created}"
            orders_text_list.append(f"<code>{order_line}</code>")
            # --- END OF FIX ---
    
    orders_text = "\n".join(orders_text_list)
    
    if not user_orders:
        final_text = f"{constants.language.no_orders_for_review}\n\n{constants.language.review_footer}"
    else:
        # We need to wrap the header and footer text to match the screenshot's style.
        final_text = (
            f"❗️ Если вы хотите оставить отзыв о конкретном заказе или товаре - просто в ответном сообщении отправьте цифрами номер этого заказа\n"
            f"➖➖\n"
            f"🍕 Список Ваших заказов:\n"
            f"➖➖\n"
            f"{orders_text}\n"
            f"➖➖\n"
            f"❗️ Если вы хотите отставить просто общий отзыв, можете сразу отправить текст Вашего отзыва в ответном сообщении\n\n"
            f"Чтобы вернуться в меню и начать сначала нажмите 👉 /start"
        )

    # Set the initial state for the review process
    await LeaveReview.waiting_for_input.set()
    
    # We MUST use parse_mode="HTML" to render the <code> tags.
    await message.answer(final_text, parse_mode="HTML", disable_web_page_preview=True)