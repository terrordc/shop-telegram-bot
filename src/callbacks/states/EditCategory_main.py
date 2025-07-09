import importlib
from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
import states
from markups import markups

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    if message:
        raise ModuleNotFoundError

    call = callback_query.data[callback_query.data.index("}")+1:]
    category = models.categories.Category(data["cid"])

    await state.update_data(category_id=category.id)
    state_data = await state.get_data()

    text = constants.language.unknown_error

    markup = []
    match call:
        case "editCategoryName":
            await states.EditCategory.name.set()
            text = constants.language.input_category_name
        case "editCategoryPC":
            await states.EditCategory.parent_category.set()
            text = constants.language.set_parent_category
            markup = [
                (await category.name, f'{{"r":"admin","pid":{category.id}}}setCategoryPC')
                for category in filter(lambda category: category.id != state_data["category_id"], await models.categories.get_categories())
            ]
            markup.append((constants.language.skip, f'{{"r":"admin","pid":0}}setCategoryPC'))
        case "deleteCategory":
            await states.EditCategory.delete.set()
            text = constants.language.confirm_delete_category
            markup = [(
                (constants.language.yes, f'{{"r":"admin"}}deleteCategory'),
                (constants.language.no, f'{{"r":"admin","d":"editCategory","cid":{category.id}}}cancel')
            )]
        case "toggleHideCategory":
            await category.set_is_hidden(not await category.is_hidden)
            await importlib.import_module("callbacks.admin.editCategory").execute(callback_query, user, data)
            return
    if call != "deleteCategory":
        markup.append((constants.language.back, f'{{"r":"admin","d":"editCategory","cid":{category.id}}}cancel'))


    await callback_query.message.edit_text(
        text=text,
        reply_markup=markups.create(markup)
    )

    

