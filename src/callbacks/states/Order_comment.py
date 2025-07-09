# from src/callbacks/states/Order_comment.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import asyncio
import models
import constants
from markups import markups
import states  # <--- FIX #1: MAKE SURE THIS IMPORT EXISTS

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    if message:
        # 1. Save the comment from the user's message
        await state.update_data(comment=message.text)
        state_data = await state.get_data()

        # 2. Get cart details for the summary
        cart_items_dict, total_price = await asyncio.gather(
            user.cart.items.dict,
            user.cart.total_price
        )
        
        items_text_list = []
        for item_id, amount in cart_items_dict.items():
            item = models.items.Item(item_id)
            item_name, item_price = await asyncio.gather(item.name, item.price)
            items_text_list.append(f"  - {item_name} ({amount} шт.) = {amount * item_price}{constants.config['settings']['currency_symbol']}")
        
        items_text = "\n".join(items_text_list)

        # 3. Create the final confirmation text
        final_text = constants.language.confirm_order_text.format(
            full_name=state_data.get('full_name', 'Не указано'),
            phone_number=state_data.get('phone_number', 'Не указано'),
            address=state_data.get('address', 'Не указан'),
            comment=state_data.get('comment', 'Нет'),
            items_text=items_text,
            total_price=total_price,
            currency_symbol=constants.config['settings']['currency_symbol']
        )

        # 4. Create the final markup
        markup = markups.create([
            (constants.language.confirm_and_pay, f'{{"r":"user"}}create_payment'),
            (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
        ])

        # 5. Show the final confirmation
        await message.answer(
            text=final_text,
            reply_markup=markup,
            parse_mode="HTML"
        )
        
        # --- FIX #2: USE THE CORRECT SYNTAX TO SET THE STATE ---
        await state.set_state(states.Order.confirmation)
    else:
        return