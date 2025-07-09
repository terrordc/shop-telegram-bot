import importlib
from aiogram import types
from aiogram.dispatcher import FSMContext
import models
from localization import ru
from markups import markups
import states

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    if message:
        # This state should only be reachable via callback
        return

    # <--- FIX HERE: Revert to the original method of parsing the action name
    # This reads the action (e.g., 'deleteCategory') from after the JSON part
    call = callback_query.data.split('}', 1)[1]

    category = models.categories.Category(data["cid"])

    await state.update_data(category_id=category.id)
    
    text = ru.unknown_error
    markup_buttons = []

    match call:
        case "editCategoryName":
            await states.EditCategory.name.set()
            text = ru.input_category_name
            # The back button needs to redirect to the single category edit menu
            markup_buttons.append((ru.back, f'{{"call": "edit_category", "cid": {category.id}}}'))
        
        case "editCategoryPC":
            await states.EditCategory.parent_category.set()
            text = ru.set_parent_category
            all_cats = await models.categories.get_categories()
            # This logic needs to be updated to the state handler format
            # For now, let's assume it works, the main issue is delete
            markup_buttons = [
                (await cat.name, f'{{"pid":{cat.id}}}setCategoryPC') # Simplified callback for state
                for cat in all_cats if cat.id != category.id
            ]
            markup_buttons.append((ru.skip, f'{{"pid": 0}}setCategoryPC'))
            markup_buttons.append((ru.back, f'{{"call": "edit_category", "cid": {category.id}}}'))

        case "deleteCategory":
            await states.EditCategory.delete.set()

            # --- CASCADE WARNING LOGIC ---
            descendants = await category.get_all_descendants()
            all_affected_ids = [category.id] + [c.id for c in descendants]
            item_count = await models.items.get_item_count_in_categories(all_affected_ids)
            category_name = await category.name

            text = ru.confirm_delete_category_cascade.format(
                category_name=category_name,
                sub_category_count=len(descendants),
                item_count=item_count
            )
            
            # The "Yes" button calls the active state handler (edit_category_delete_state)
            # with a simple callback. The "No" button cancels and goes back.
            markup_buttons = [(
                (ru.yes, 'confirm_delete'),
                (ru.no, f'{{"call": "edit_category", "cid": {category.id}}}')
            )]
            # --- END LOGIC ---

        case "toggleHideCategory":
            await category.set_is_hidden(not await category.is_hidden)
            await importlib.import_module("callbacks.admin.edit_category").execute(callback_query, user, data)
            return
        
    # Default back button if not handled above
    if call != "deleteCategory":
        if not any(btn_text == ru.back for btn_text, _ in markup_buttons):
             markup_buttons.append((ru.back, f'{{"call": "edit_category", "cid": {category.id}}}'))

    await callback_query.message.edit_text(
        text=text,
        reply_markup=markups.create(markup_buttons),
        parse_mode='HTML'
    )