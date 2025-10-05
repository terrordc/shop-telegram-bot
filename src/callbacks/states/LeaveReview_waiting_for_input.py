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
        await state.update_data(order_id=int(user_input))
        await LeaveReview.waiting_for_text.set()
        # --- ADD THE FOOTER HERE ---
        await message.answer(f"{constants.language.review_request_text}\n\n{constants.language.review_text_limits}{constants.language.review_state_footer}")

    # Case 2: User sent general review text
    else:
        if not (5 <= len(user_input) <= 255):
            await message.answer(constants.language.review_invalid_text)
            return

        await state.update_data(order_id=None, review_text=user_input)
        await LeaveReview.waiting_for_rating.set()
        # --- AND ADD THE FOOTER HERE ---
        await message.answer(f"{constants.language.review_request_rating}{constants.language.review_state_footer}")