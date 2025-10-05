# callbacks/states/LeaveReview_waiting_for_input.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from states import LeaveReview

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message, state: FSMContext) -> None:
    user_input = message.text

    # Check if input is a valid order ID
    if user_input.isdigit():
        order_id = int(user_input)
        # Here you might want to add a check if this order actually belongs to the user
        # For simplicity, we'll trust the user for now.
        await state.update_data(order_id=order_id)
        await LeaveReview.next() # Moves to waiting_for_rating
        await message.answer(f"{constants.language.review_request_text}\n\n{constants.language.review_text_limits}")
        # After getting order ID, we need the review text, so we set a new state
        await LeaveReview.waiting_for_rating.set() # Re-using this state name, but it's for text now

    # If it's not a number, treat it as general review text
    else:
        if not (5 <= len(user_input) <= 255):
            return await message.answer(constants.language.review_invalid_text)
        
        await state.update_data(order_id=None, review_text=user_input)
        await LeaveReview.waiting_for_rating.set()
        await message.answer(constants.language.review_request_rating)