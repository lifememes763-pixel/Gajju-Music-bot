from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums import ButtonStyle
from SHUKLAMUSIC import app
from SHUKLAMUSIC.utils.database import get_lang, set_lang
from SHUKLAMUSIC.utils.decorators import ActualAdminCB, language, languageCB
from config import BANNED_USERS
from strings import get_string, languages_present


def lanuages_keyboard(_, current_lang=None):
    buttons = []

    for i in languages_present:
        buttons.append(
            InlineKeyboardButton(
                text=languages_present[i],
                callback_data=f"languages:{i}",
                style=(
                    ButtonStyle.SUCCESS
                    if str(i) == str(current_lang)
                    else ButtonStyle.PRIMARY
                ),
            )
        )

    keyboard = []
    for i in range(0, len(buttons), 2):
        keyboard.append(buttons[i:i + 2])

    keyboard.append(
        [
            InlineKeyboardButton(
                text=_["BACK_BUTTON"],
                callback_data="settingsback_helper",
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
                style=ButtonStyle.DANGER,
            ),
        ]
    )

    return InlineKeyboardMarkup(keyboard)


@app.on_message(
    filters.command(["lang", "setlang", "language"]) & ~BANNED_USERS
)
@language
async def langs_command(client, message: Message, _):
    current_lang = await get_lang(message.chat.id)
    keyboard = lanuages_keyboard(_, current_lang)

    await message.reply_text(
        _["lang_1"],
        reply_markup=keyboard,
    )


@app.on_callback_query(filters.regex("LG") & ~BANNED_USERS)
@languageCB
async def lanuagecb(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except Exception:
        pass

    current_lang = await get_lang(CallbackQuery.message.chat.id)
    keyboard = lanuages_keyboard(_, current_lang)

    return await CallbackQuery.edit_message_reply_markup(
        reply_markup=keyboard
    )


@app.on_callback_query(
    filters.regex(r"languages:(.*?)") & ~BANNED_USERS
)
@ActualAdminCB
async def language_markup(client, CallbackQuery, _):
    langauge = CallbackQuery.data.split(":", 1)[1]
    chat_id = CallbackQuery.message.chat.id

    old = await get_lang(chat_id)

    if str(old) == str(langauge):
        return await CallbackQuery.answer(
            _["lang_4"],
            show_alert=True,
        )

    try:
        new_strings = get_string(langauge)
        await set_lang(chat_id, langauge)

        await CallbackQuery.answer(
            new_strings["lang_2"],
            show_alert=True,
        )

        keyboard = lanuages_keyboard(new_strings, langauge)

    except Exception:
        return await CallbackQuery.answer(
            _["lang_3"],
            show_alert=True,
        )

    return await CallbackQuery.edit_message_reply_markup(
        reply_markup=keyboard
    )
