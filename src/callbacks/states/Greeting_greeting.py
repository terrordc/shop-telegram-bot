from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    constants.config.set(("info", "greeting"), message.text)

    await message.answer(
        text=constants.language.greeting_was_set,
        reply_markup=markups.create([
            (constants.language.back, f"{constants.JSON_ADMIN}main_settings")
        ])
    )
    
    await state.finish()

