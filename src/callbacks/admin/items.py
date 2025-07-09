from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    text = constants.language.item_management
    markup = markups.create([
        (constants.language.add_item, f"{constants.JSON_ADMIN}add_item"),
        (constants.language.edit_item, f"{constants.JSON_ADMIN}editItemsCategories"),
        (constants.language.back, f"{constants.JSON_ADMIN}adminPanel")
    ])


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

