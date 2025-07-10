# src/callbacks/admin/items.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    text = constants.language.item_management
    
    markup = markups.create([
        (constants.language.add_item, f"{constants.JSON_ADMIN}add_item"),
        # --- FIX: Changed the destination from 'editItemsCategories' to 'all_items' ---
        (constants.language.edit_item, f"{constants.JSON_ADMIN}all_items"),
        (constants.language.back, f"{constants.JSON_ADMIN}adminPanel")
    ])

    # The rest of the function is fine
    try: 
        await callback_query.message.edit_text(
            text=text,
            reply_markup=markup
        )
    except:
        await callback_query.message.delete()
        await callback_query.message.answer(
            text=text,
            reply_markup=markup
        )