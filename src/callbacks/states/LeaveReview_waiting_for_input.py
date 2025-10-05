# callbacks/states/LeaveReview_waiting_for_input.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from states import LeaveReview

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message, state: FSMContext) -> None:
    user_input = message.text

    # --- START OF CHANGE ---
    # This logic now handles both "/123" (from link click) and "123" (from manual typing)
    
    order_id_str = user_input
    # If the input is a command link, extract just the number part.
    if user_input.startswith('/') and user_input[1:].isdigit():
        order_id_str = user_input[1:]

    # Now, check if the result is a number.
    if order_id_str.isdigit():
        # Case 1: User provided an Order ID
        order_id = int(order_id_str)
        await state.update_data(order_id=order_id)
        await LeaveReview.waiting_for_text.set()
        await message.answer(f"{constants.language.review_request_text_full}{constants.language.review_state_footer}")

    # --- END OF CHANGE ---
    
    else:
        # Case 2: User sent general review text
        if not (5 <= len(user_input) <= 255):
            await message.answer(constants.language.review_invalid_text)
            return # Stay in the current state to let the user try again

        await state.update_data(order_id=None, review_text=user_input)
        await LeaveReview.waiting_for_rating.set()
        await message.answer(f"{constants.language.review_request_rating}{constants.language.review_state_footer}")