from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
import importlib


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    await user.cart.items.clear()

    await importlib.import_module("callbacks.user.cart").execute(callback_query, user, data)


