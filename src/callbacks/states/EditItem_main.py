import asyncio
import importlib
from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
import states


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message: types.Message = None, state: FSMContext = None) -> None:
    if message:
        raise ModuleNotFoundError

    call = callback_query.data[callback_query.data.index("}")+1:]
    item = models.items.Item(data["iid"])
    await state.update_data(item_id=item.id)

    item_image_id = await item.image_id

    text = constants.language.unknown_error

    markup = []
    match call:
        case "editItemName":
            await states.EditItem.name.set()
            text = constants.language.input_item_name
        case "editItemDescription":
            await states.EditItem.description.set()
            text = constants.language.input_item_description
        case "editItemCategory":
            await states.EditItem.category.set()
            text = constants.language.select_item_category
            markup = [
                (await category.name, f'{{"r":"admin","cid":{category.id}}}setItemCategory')
                for category in await models.categories.get_categories()
            ]
        case "editItemPrice":
            await states.EditItem.price.set()
            text = constants.language.input_item_price
        case "editItemImage":
            await states.EditItem.image_id.set()
            if item_image_id:
                markup.append((constants.language.delete_image, f"{constants.JSON_ADMIN}deleteItemImage"))
            text = constants.language.send_item_changed_images
        case "toggleIsHidden":
            await item.set_is_hidden(not await item.is_hidden)
            await importlib.import_module("callbacks.admin.editItem").execute(callback_query, user, data, message)
            return
        case "deleteItem":
            await states.EditItem.delete.set()
            text = constants.language.confirm_delete_item
            markup = [(
                (constants.language.yes, f"{constants.JSON_ADMIN}deleteItem"),
                (constants.language.no, f'{{"r":"admin","iid":{item.id},"d":"editItem"}}cancel')
            )]
    if call != "deleteItem":
        markup.append((constants.language.back, f'{{"r":"admin","iid":{item.id},"d":"editItem"}}cancel'))

    markup = markups.create(markup)

    try:
        await callback_query.message.edit_text(
            text=text,
            reply_markup=markup
        )
    except:
        await callback_query.message.delete()
        await callback_query.message.answer(
            text=text,
            reply_markup=markup
        )


