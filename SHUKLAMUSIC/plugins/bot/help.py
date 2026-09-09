# ----------------------------------------------
# 🔸 StrangerMusic Project
# 🔹 Developed & Maintained by: Shashank Shukla (https://github.com/itzshukla)
# 📅 Copyright © 2022 – All Rights Reserved
#
# 📖 License:
# This source code is open for educational and non-commercial use ONLY.
# You are required to retain this credit in all copies or substantial portions of this file.
# Commercial use, redistribution, or removal of this notice is strictly prohibited
# without prior written permission from the author.
#
# ❤️ Made with dedication and love by ItzShukla
# -----------------------------------------------
import random
from typing import Union
from pyrogram import filters, types, enums
from pyrogram.types import InlineKeyboardMarkup, Message, InlineKeyboardButton
from SHUKLAMUSIC import app
from SHUKLAMUSIC.utils import help_pannel
from SHUKLAMUSIC.utils.database import get_lang
from SHUKLAMUSIC.utils.decorators.language import LanguageStart, languageCB
from SHUKLAMUSIC.utils.inline.help import help_back_markup, private_help_panel
from SHUKLAMUSIC.utils.inline.start import start_panel
from config import BANNED_USERS, START_IMG_URL, SUPPORT_CHAT
from strings import get_string, helpers
from SHUKLAMUSIC.utils.stuffs.buttons import BUTTONS
from SHUKLAMUSIC.utils.stuffs.helper import Helper

# 🖼️ Code ke andar hi SHASHANK_IMG ki list bana di gayi hai
SHASHANK_IMG = [
    "https://i.ibb.co/bRFNr2Qy/g-Ps-ZKm-Ma.jpg",
    "https://i.ibb.co/yFHCgpRG/p5-Vg-N6-Au.jpg",
    "https://i.ibb.co/bgzQ2YV1/v-Y9z-JCSF.jpg",
]


@app.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("settings_back_helper") & ~BANNED_USERS)
async def helper_private(
    client: app, update: Union[types.Message, types.CallbackQuery]
):
    is_callback = isinstance(update, types.CallbackQuery)
    if is_callback:
        try:
            await update.answer()
        except Exception:
            pass
        chat_id = update.message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)
        keyboard = help_pannel(_, True)
        await update.edit_message_text(
            _["help_1"].format(SUPPORT_CHAT), reply_markup=keyboard
        )
    else:
        language = await get_lang(update.chat.id)
        _ = get_string(language)
        keyboard = help_pannel(_)
        await update.reply_photo(
            random.choice(SHASHANK_IMG),
            caption=_["help_1"].format(SUPPORT_CHAT),
            reply_markup=keyboard,
        )


# -----------------------------------------------
# 🔸 NEW WELCOME BACK HANDLER (Settingsback_helper)
# -----------------------------------------------
from pyrogram.types import InputMediaPhoto

@app.on_callback_query(filters.regex("^Settingsback_helper$") & ~BANNED_USERS)
async def Settingsback_helper(client, CallbackQuery):
    try:
        await CallbackQuery.answer()
    except Exception:
        pass

    chat_id = CallbackQuery.message.chat.id
    language = await get_lang(chat_id)
    _ = get_string(language)

    # 1. Welcome Text (Start Caption)
    welcome_text = _["start_2"].format(
        CallbackQuery.from_user.mention,
        app.mention,
    )

    # 2. Welcome Buttons
    from SHUKLAMUSIC.utils.inline.start import start_panel
    keyboard = start_panel(_)

    # 3. Photo Media edit karna (jisse Photo + Caption + Buttons sab wapas aa jaye)
    try:
        await CallbackQuery.edit_message_media(
            media=InputMediaPhoto(
                media=START_IMG_URL,
                caption=welcome_text,
            ),
            reply_markup=keyboard,
        )
    except Exception:
        # Fallback: agar pehle se sirf caption edit ho sakta ho
        try:
            await CallbackQuery.edit_message_caption(
                caption=welcome_text,
                reply_markup=keyboard,
            )
        except Exception:
            pass

@app.on_message(filters.command(["help"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client, message: Message, _):
    keyboard = private_help_panel(_)
    await message.reply_text(
        _["help_2"], 
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


@app.on_callback_query(filters.regex("help_callback") & ~BANNED_USERS)
@languageCB
async def helper_cb(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    cb = callback_data.split(None, 1)[1]
    keyboard = help_back_markup(_)
    if cb == "hb1":
        await CallbackQuery.edit_message_text(helpers.HELP_1, reply_markup=keyboard)
    elif cb == "hb2":
        await CallbackQuery.edit_message_text(helpers.HELP_2, reply_markup=keyboard)
    elif cb == "hb3":
        await CallbackQuery.edit_message_text(helpers.HELP_3, reply_markup=keyboard)
    elif cb == "hb4":
        await CallbackQuery.edit_message_text(helpers.HELP_4, reply_markup=keyboard)
    elif cb == "hb5":
        await CallbackQuery.edit_message_text(helpers.HELP_5, reply_markup=keyboard)
    elif cb == "hb6":
        await CallbackQuery.edit_message_text(helpers.HELP_6, reply_markup=keyboard)
    elif cb == "hb7":
        await CallbackQuery.edit_message_text(helpers.HELP_7, reply_markup=keyboard)
    elif cb == "hb8":
        await CallbackQuery.edit_message_text(helpers.HELP_8, reply_markup=keyboard)
    elif cb == "hb9":
        await CallbackQuery.edit_message_text(helpers.HELP_9, reply_markup=keyboard)
    elif cb == "hb10":
        await CallbackQuery.edit_message_text(helpers.HELP_10, reply_markup=keyboard)
    elif cb == "hb11":
        await CallbackQuery.edit_message_text(helpers.HELP_11, reply_markup=keyboard)
    elif cb == "hb12":
        await CallbackQuery.edit_message_text(helpers.HELP_12, reply_markup=keyboard)
    elif cb == "hb13":
        await CallbackQuery.edit_message_text(helpers.HELP_13, reply_markup=keyboard)
    elif cb == "hb14":
        await CallbackQuery.edit_message_text(helpers.HELP_14, reply_markup=keyboard)
    elif cb == "hb15":
        await CallbackQuery.edit_message_text(helpers.HELP_15, reply_markup=keyboard)
    elif cb == "hb16":
        await CallbackQuery.edit_message_text(helpers.HELP_16, reply_markup=keyboard)
    elif cb == "hb17":
        await CallbackQuery.edit_message_text(helpers.HELP_17, reply_markup=keyboard)
    elif cb == "hb18":
        await CallbackQuery.edit_message_text(helpers.HELP_18, reply_markup=keyboard)
    elif cb == "hb19":
        await CallbackQuery.edit_message_text(helpers.HELP_19, reply_markup=keyboard)
    elif cb == "hb20":
        await CallbackQuery.edit_message_text(helpers.HELP_20, reply_markup=keyboard)
    elif cb == "hb21":
        await CallbackQuery.edit_message_text(helpers.HELP_21, reply_markup=keyboard)


@app.on_callback_query(filters.regex("mbot_cb") & ~BANNED_USERS)
async def helper_cb_mbot(client, CallbackQuery):
    try:
        await CallbackQuery.answer()
    except Exception:
        pass
    await CallbackQuery.edit_message_text(Helper.HELP_M, reply_markup=InlineKeyboardMarkup(BUTTONS.MBUTTON))


@app.on_callback_query(filters.regex("^managebot123") & ~BANNED_USERS)
async def on_back_button(client, CallbackQuery):
    try:
        await CallbackQuery.answer()
    except Exception:
        pass
    chat_id = CallbackQuery.message.chat.id
    language = await get_lang(chat_id)
    _ = get_string(language)
    keyboard = help_pannel(_, True)
    await CallbackQuery.edit_message_text(
        _["help_1"].format(SUPPORT_CHAT), reply_markup=keyboard
    )


@app.on_callback_query(filters.regex("^mplus") & ~BANNED_USERS)      
async def mb_plugin_button(client, CallbackQuery):
    try:
        await CallbackQuery.answer()
    except Exception:
        pass
    callback_data = CallbackQuery.data.strip()
    split_data = callback_data.split(None, 1)
    
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="mbot_cb")]])
    
    if len(split_data) > 1:
        cb = split_data[1]
        if cb == "Okieeeeee":
            await CallbackQuery.edit_message_text("`something errors`", reply_markup=keyboard, parse_mode=enums.ParseMode.MARKDOWN)
        else:
            text = getattr(Helper, cb, "`No help text available.`")
            await CallbackQuery.edit_message_text(text, reply_markup=keyboard)
    else:
        await CallbackQuery.edit_message_text(Helper.HELP_M, reply_markup=InlineKeyboardMarkup(BUTTONS.MBUTTON))
    
