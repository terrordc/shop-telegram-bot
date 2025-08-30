# Create this new file: src/callbacks/states/Order_full_name.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
import states

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    full_name = message.text
    
    # --- START OF VALIDATION LOGIC ---
    name_parts = full_name.split()
    
    # Rule: At least 2 words, and each word is at least 2 characters long.
    is_valid = len(name_parts) >= 2 and all(len(part) >= 2 for part in name_parts)

    if not is_valid:
        # If the name is invalid, send an error and STAY in the current state.
        await message.answer(
            "Пожалуйста, введите настоящие имя и фамилию (например: Иван Иванов).",
            reply_markup=markups.create(
                [(constants.language.back, f'{{"r":"user","d":"cart"}}cancel')]
            )
        )
        return # Stop processing
    # --- END OF VALIDATION LOGIC ---

    # 1. If validation passes, save the full name
    await state.update_data(full_name=full_name)

    # 2. Determine the next step in the flow (this part is correct)
    checkout_settings = constants.config['checkout']
    text = constants.language.unknown_error

    if checkout_settings["phone"]:
        text = constants.language.input_phone
        await states.Order.phone_number.set()
    elif checkout_settings["address"]:
        text = constants.language.input_address
        await states.Order.address.set()
    else:
        text = constants.language.input_comment
        await states.Order.comment.set()
        
    # 3. Ask for the next piece of information
    await message.answer(
        text=text,
        reply_markup=markups.create([
            (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
        ]),
        parse_mode="HTML"
    )