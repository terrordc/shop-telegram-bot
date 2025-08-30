# from callbacks/states/Order_address.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
import states

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    address_text = message.text

    # --- START OF ADDRESS VALIDATION LOGIC ---
    # Rule 1: Must be at least 10 characters long.
    is_long_enough = len(address_text) >= 10
    # Rule 2: Must contain at least 2 words.
    has_enough_words = len(address_text.split()) >= 2
    # Rule 3: Must contain at least one digit.
    has_a_digit = any(char.isdigit() for char in address_text)

    if not (is_long_enough and has_enough_words and has_a_digit):
        # If the address is invalid, send an error and STAY in the current state.
        await message.answer(
            "Пожалуйста, введите полный и корректный адрес (город, улица, дом). Например: г. Москва, ул. Ленина, д. 15, кв. 5",
            reply_markup=markups.create(
                [(constants.language.back, f'{{"r":"user","d":"cart"}}cancel')]
            )
        )
        return # Stop processing
    # --- END OF ADDRESS VALIDATION LOGIC ---

    # 1. If validation passes, save the address
    await state.update_data(address=address_text)

    # 2. Determine the next step in the checkout process (this part is correct)
    checkout_settings = constants.config['checkout']
    text = constants.language.unknown_error

    if checkout_settings.get("captcha", False):
        text = constants.language.input_captcha
        await states.Order.captcha.set()
    else:
        text = constants.language.input_comment
        await states.Order.comment.set()

    # 3. Ask for the next piece of information
    await message.answer(
        text=text,
        reply_markup=markups.create([
            (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
        ])
    )