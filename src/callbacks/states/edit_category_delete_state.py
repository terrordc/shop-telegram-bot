import importlib
from aiogram import types
from aiogram.dispatcher import FSMContext
import models
from localization import ru
from markups import markups

async def execute(message: types.Message, user: models.users.User, data: dict, state: FSMContext, callback_query: types.CallbackQuery = None) -> None:
    if callback_query:
        # This handles the "Yes" button press
        state_data = await state.get_data()
        category_id = state_data.get("category_id")
        
        if not category_id:
            await state.finish()
            # Redirect to the main category list if something went wrong
            await importlib.import_module("callbacks.admin.edit_categories").execute(callback_query=callback_query, user=user, data=data)
            return

        category = models.categories.Category(category_id)
        category_name = await category.name

        # Perform the actual deletion
        await category.cascade_delete()
        
        await state.finish()
        
        # Notify the admin of success
        await callback_query.message.edit_text(ru.category_deleted_successfully.format(category_name=category_name))
        
        # Show the updated list of all categories
        await importlib.import_module("callbacks.admin.edit_categories").execute(callback_query=callback_query, user=user, data={"call": "edit_categories"})
    else:
        # If the user sends a text message instead of pressing a button
        await message.answer("Пожалуйста, используйте кнопки для подтверждения.", reply_markup=message.reply_markup)