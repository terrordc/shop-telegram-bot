# callbacks/states/LeaveReview_waiting_for_rating.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import models.reviews
import constants

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message, state: FSMContext) -> None:
    rating_input = message.text

    if not rating_input.isdigit() or not (1 <= int(rating_input) <= 5):
        await message.answer(constants.language.review_invalid_rating)
        return

    state_data = await state.get_data()

    await models.reviews.create(
        user_id=user.id,
        review_text=state_data['review_text'],
        rating=int(rating_input),
        order_id=state_data.get('order_id')
    )

    # --- ADD THE FOOTER HERE ---
    await message.answer(f"{constants.language.review_thanks}{constants.language.review_state_footer}")
    await state.finish()