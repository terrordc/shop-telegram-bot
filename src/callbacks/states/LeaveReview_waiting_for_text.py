# callbacks/states/LeaveReview_waiting_for_text.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from states import LeaveReview

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message, state: FSMContext) -> None:
    review_text = message.text
    
    if not (5 <= len(review_text) <= 255):
        await message.answer(constants.language.review_invalid_text)
        return

    await state.update_data(review_text=review_text)
    await LeaveReview.waiting_for_rating.set()
    # --- ADD THE FOOTER HERE ---
    # callbacks/states/LeaveReview_waiting_for_text.py

# ... (imports)

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message, state: FSMContext) -> None:
    review_text = message.text
    
    if not (5 <= len(review_text) <= 255):
        await message.answer(constants.language.review_invalid_text)
        return

    await state.update_data(review_text=review_text)
    await LeaveReview.waiting_for_rating.set()
    
    # --- START OF FIX ---
    # Use the new, single string here as well
    await message.answer(f"{constants.language.review_request_rating}{constants.language.review_state_footer}")
    # --- END OF FIX ---