# callbacks/states/LeaveReview_waiting_for_rating.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import models.reviews
import constants

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message, state: FSMContext) -> None:
    rating_input = message.text

    # 1. Validate the rating
    if not rating_input.isdigit() or not (1 <= int(rating_input) <= 5):
        await message.answer(constants.language.review_invalid_rating)
        return # Stay in this state and let the user try again

    # 2. Get all the data we've collected
    state_data = await state.get_data()

    # 3. Save the review to the database
    await models.reviews.create(
        user_id=user.id,
        review_text=state_data['review_text'],
        rating=int(rating_input),
        order_id=state_data.get('order_id') # .get() safely handles general reviews
    )

    # 4. Thank the user and FINISH the state
    await message.answer(constants.language.review_thanks)
    await state.finish()