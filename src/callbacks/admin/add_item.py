# src/callbacks/admin/add_item.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import models # No longer need models.categories
import constants
from markups import markups
from states import AddItem # Import the specific state group

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    # The old logic checking for categories has been completely removed.
    # We now go directly to asking for the item name.

    await callback_query.message.edit_text(
        text=constants.language.input_item_name,
        reply_markup=markups.create([
            (constants.language.back, f'{{"r":"admin","d":"items"}}cancel')
        ])
    )

    # Set the state to wait for the user's next message, which will be the item name.
    await AddItem.name.set()