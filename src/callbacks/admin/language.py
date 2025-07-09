from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
import states


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    await callback_query.message.edit_text(
        text=constants.language.choose_a_language,
        reply_markup=markups.create([
            (constants.language.english, f"{constants.JSON_ADMIN}en"),
            (constants.language.russian, f"{constants.JSON_ADMIN}ru"),
            (constants.language.back, f'{{"r":"admin", "d":"main_settings"}}cancel')
        ])
    )

    await states.Language.language.set()

