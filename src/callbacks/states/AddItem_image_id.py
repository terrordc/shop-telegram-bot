# src/callbacks/states/AddItem_image_id.py

from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
from states import AddItem # Use the specific state group

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    state_data = await state.get_data()

    # --- FIX ---
    # This function now builds the confirmation text WITHOUT the category.
    def format_text(image_id_str: str) -> str:
        # NOTE: You may need to adjust the language file constant 'format_confirm_item'
        # to remove any reference to a category.
        return constants.language.format_confirm_item(
            state_data.get('name', 'N/A'), 
            state_data.get('description', 'N/A'), 
            state_data.get('price', 0.0), 
            image_id_str
        )

    markup = markups.create([
        [(constants.language.yes, f'{constants.JSON_ADMIN}confirm'), (constants.language.no, f'{{"r":"admin","d":"items"}}cancel')]
    ])

    if message and message.photo:
        # This part handles receiving the photo message
        file_id = message.photo[-1].file_id
        await state.update_data(image_id=file_id)
        await message.answer_photo(
            photo=file_id,
            caption=format_text(file_id),
            reply_markup=markup
        )
    elif callback_query:
        # This part handles the "Skip" button press
        call = callback_query.data[callback_query.data.index("}")+1:]
        if call == "skip":
            await state.update_data(image_id=None)
            await callback_query.message.edit_text(
                text=format_text("None"),
                reply_markup=markup
            )
        else:
            # Ignore other callbacks
            return await callback_query.answer()
    else:
        # If we receive a text message or something else, ignore it.
        return

    # Set the final state to wait for the user to press "Yes" or "No"
    await AddItem.confirmation.set()