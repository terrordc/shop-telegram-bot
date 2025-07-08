
from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
import states
import re


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, state: FSMContext, message: types.Message=None) -> None:
    # FIX 2: Updated regex to accept numbers starting with +7, 8, or 7, followed by 10 digits.
    if not re.match(r"^(?:\+7|8|7)\d{10}$", message.text):
        # FIX 1: Use the correct language key 'input_phone_error' instead of 'invalid_phone_number'.
        await message.answer(constants.language.input_phone_error)
        return

    await state.update_data(phone_number=message.text)

    checkout_settings = constants.config['checkout']

    text = constants.language.unknown_error
    if checkout_settings["address"]:
        text = constants.language.input_address
        await states.Order.address.set()
    else:
        text = constants.language.input_comment
        await states.Order.comment.set()

    await message.answer(
        text=text,
        reply_markup=markups.create([
            (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
        ]),
        parse_mode="HTML"  # <-- ADD THIS LINE
    )