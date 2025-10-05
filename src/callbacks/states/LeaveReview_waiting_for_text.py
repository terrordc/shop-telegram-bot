# callbacks/states/LeaveReview_waiting_for_text.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from states import LeaveReview

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message, state: FSMContext) -> None:
    review_text = message.text
    
    # Validate the text length
    if not (5 <= len(review_text) <= 255):
        await message.answer(constants.language.review_invalid_text)
        return # Stay in this state and let the user try again

    # Save the text and move to the final state: getting the rating
    await state.update_data(review_text=review_text)
    await LeaveReview.waiting_for_rating.set()
    await message.answer(constants.language.review_request_rating)