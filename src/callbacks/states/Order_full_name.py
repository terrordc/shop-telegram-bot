# Create this new file: src/callbacks/states/Order_full_name.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
import states

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    # 1. Save the full name from the user's message
    await state.update_data(full_name=message.text)

    # 2. Determine the next step in the flow
    checkout_settings = constants.config['checkout']
    text = constants.language.unknown_error

    if checkout_settings["phone"]:
        text = constants.language.input_phone
        await states.Order.phone_number.set()
    elif checkout_settings["address"]:
        text = constants.language.input_address
        await states.Order.address.set()
    # ... etc., continuing the chain ...
    else:
        text = constants.language.input_comment
        await states.Order.comment.set()
        
    # 3. Ask for the next piece of information
    await message.answer(
        text=text,
        reply_markup=markups.create([
            (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
        ]),
        parse_mode="HTML" # Use HTML for prompts with examples
    )