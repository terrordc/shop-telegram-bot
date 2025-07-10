from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    text = constants.language.admin_panel
    markup = markups.create([
        (constants.language.item_management, f"{constants.JSON_ADMIN}items"),
        (constants.language.user_management, f"{constants.JSON_ADMIN}users"),
        # (constants.language.stats, f"{constants.JSON_ADMIN}stats"),
        (constants.language.orders, f'{constants.JSON_ADMIN}orders'),
        (constants.language.settings, f"{constants.JSON_ADMIN}settings"),
    ])

    if message:
        return await message.answer(text, reply_markup=markup)
    await callback_query.message.edit_text(text, reply_markup=markup)

