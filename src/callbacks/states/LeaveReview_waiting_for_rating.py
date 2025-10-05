# callbacks/states/LeaveReview_waiting_for_rating.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message, state: FSMContext) -> None:
    state_data = await state.get_data()
    
    # Scenario 1: We just got the review text for a specific order
    if "review_text" not in state_data:
        review_text = message.text
        if not (5 <= len(review_text) <= 255):
            return await message.answer(constants.language.review_invalid_text)
        
        await state.update_data(review_text=review_text)
        await message.answer(constants.language.review_request_rating)
        return # Wait for the rating

    # Scenario 2: We just got the rating
    rating_input = message.text
    if not rating_input.isdigit() or not (1 <= int(rating_input) <= 5):
        return await message.answer(constants.language.review_invalid_rating)

    # We have all data, save the review
    await models.reviews.create(
        user_id=user.id,
        review_text=state_data['review_text'],
        rating=int(rating_input),
        order_id=state_data.get('order_id') # .get() handles the case of a general review
    )

    await message.answer(constants.language.review_thanks)
    await state.finish()