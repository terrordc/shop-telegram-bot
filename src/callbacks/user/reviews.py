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
    # 1. Get the bot's own username dynamically
    bot_username = (await message.bot.get_me()).username
    
    # 2. Construct the full footer with the bot's username
    full_footer = (
        f"❗️ Если вы хотите отставить просто общий отзыв, можете сразу отправить текст Вашего отзыва в ответном сообщении\n\n"
        f"Чтобы вернуться в меню и начать сначала нажмите 👉 /start или @{bot_username}"
    )
    # --- END OF FIX ---

    if not user_orders:
        final_text = f"{constants.language.no_orders_for_review}\n\n{constants.language.review_footer}" # Note: review_footer will now be replaced by full_footer
        # For consistency, let's use the full_footer here too
        final_text = f"{constants.language.no_orders_for_review}\n\n{full_footer}"
    else:
        final_text = (
            f"❗️ Если вы хотите оставить отзыв о конкретном заказе или товаре - просто в ответном сообщении отправьте цифрами номер этого заказа\n"
            f"➖➖\n"
            f"🍕 Список Ваших заказов:\n"
            f"➖➖\n"
            f"{orders_text}\n"
            f"➖➖\n"
            f"{full_footer}" # Use the new footer here
        )

    await LeaveReview.waiting_for_input.set()
    await message.answer(final_text, parse_mode="HTML", disable_web_page_preview=True)