from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    text = constants.config["info"]["refund_policy"]
    markup = markups.create([
        (constants.language.back, f"{constants.JSON_USER}faq")
    ])

    if message:
        return await message.answer(text, reply_markup=markup)
    await callback_query.message.edit_text(text, reply_markup=markup)


