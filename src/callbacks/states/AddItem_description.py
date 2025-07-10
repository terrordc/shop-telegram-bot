from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
from states import AddItem # Use the specific state group

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    # This handler should only receive a message (the description)
    if not message:
        return

    # Save the description to the state
    await state.update_data(description=message.text)

    # --- FIX ---
    # Instead of asking for a category, we now ask for the price.
    await message.answer(
        text=constants.language.input_item_price,
        reply_markup=markups.create([
            (constants.language.back, f'{{"r":"admin","d":"items"}}cancel')
        ])
    )

    # Set the state to wait for the price
    await AddItem.price.set()