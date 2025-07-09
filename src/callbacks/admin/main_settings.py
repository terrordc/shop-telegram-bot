from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    await callback_query.message.edit_text(
        text=constants.language.main_settings,
        reply_markup=markups.create([
            (constants.language.language, f"{constants.JSON_ADMIN}language"),
            (constants.language.greeting, f"{constants.JSON_ADMIN}greeting"),
            (constants.language.back, f"{constants.JSON_ADMIN}settings")
        ])
    )

