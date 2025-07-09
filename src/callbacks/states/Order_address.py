# from callbacks/states/Order_address.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
import states

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    # 1. Save the address the user just sent
    await state.update_data(address=message.text)

    # 2. Determine the next step in the checkout process
    checkout_settings = constants.config['checkout']
    text = constants.language.unknown_error

    # Based on your config, email and captcha are disabled. The next step is the comment.
    # This logic checks for captcha just in case you enable it later.
    if checkout_settings.get("captcha", False):
        text = constants.language.input_captcha
        await states.Order.captcha.set()
    else:
        text = constants.language.input_comment
        await states.Order.comment.set()

    # --- FIX IS HERE ---
    # This state was triggered by a user message, so callback_query is None.
    # We must use message.answer() to reply with a new message.
    await message.answer(
        text=text,
        reply_markup=markups.create([
            (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
        ])
    )