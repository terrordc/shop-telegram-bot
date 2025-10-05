# callbacks/states/LeaveReview_waiting_for_input.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from states import LeaveReview

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message, state: FSMContext) -> None:
    user_input = message.text

    # Case 1: User sent an Order ID
    if user_input.isdigit():
        # You can add a check here to ensure the order belongs to the user
        await state.update_data(order_id=int(user_input))
        # Now move to the state for getting the review TEXT
        await LeaveReview.waiting_for_text.set()
        await message.answer(f"{constants.language.review_request_text}\n\n{constants.language.review_text_limits}")

    # Case 2: User sent general review text
    else:
        if not (5 <= len(user_input) <= 255):
            await message.answer(constants.language.review_invalid_text)
            return # Stay in the current state to let the user try again

        await state.update_data(order_id=None, review_text=user_input)
        # Now move to the state for getting the RATING
        await LeaveReview.waiting_for_rating.set()
        await message.answer(constants.language.review_request_rating)