# src/callbacks/user/confirm_cancellation.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    order_id = data["oid"]
    
    # Define callbacks for the Yes/No buttons
    yes_callback = f'{{"r":"user", "oid":{order_id}}}request_cancellation'
    no_callback = f'{{"r":"user", "oid":{order_id}}}order_details' # "No" just goes back to the details view

    markup = markups.create([
        (constants.language.yes_im_sure, yes_callback),
        (constants.language.no_go_back, no_callback)
    ])

    await callback_query.message.edit_text(
        text=constants.language.confirm_cancellation_prompt.format(order_id=order_id),
        reply_markup=markup
    )