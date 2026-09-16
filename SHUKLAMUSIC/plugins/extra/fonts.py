# -----------------------------------------------
# 🔸 StrangerMusic Project
# 🔹 Developed & Maintained by: Shashank Shukla
# 📅 Copyright © 2022 – All Rights Reserved
# -----------------------------------------------

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ButtonStyle

from SHUKLAMUSIC.utils.Shukla_font import Fonts
from SHUKLAMUSIC import app


FONT_TEXTS = {}


def first_page_buttons():
    return [
        [
            InlineKeyboardButton("𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛", callback_data="style+typewriter", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("𝕆𝕦𝕥𝕝𝕚𝕟𝕖", callback_data="style+outline", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("𝐒𝐞𝐫𝐢𝐟", callback_data="style+serif", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("𝑺𝒆𝒓𝒊𝒇", callback_data="style+bold_cool", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("𝑆𝑒𝑟𝑖𝑓", callback_data="style+cool", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("Sᴍᴀʟʟ Cᴀᴘs", callback_data="style+small_cap", style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton("𝓈𝒸𝓇𝒾𝓅𝓉", callback_data="style+script", style=ButtonStyle.DANGER),
            InlineKeyboardButton("𝓼𝓬𝓻𝓲𝓹𝓽", callback_data="style+script_bolt", style=ButtonStyle.DANGER),
            InlineKeyboardButton("ᵗⁱⁿʸ", callback_data="style+tiny", style=ButtonStyle.DANGER),
        ],
        [
            InlineKeyboardButton("ᑕOᗰIᑕ", callback_data="style+comic", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("𝗦𝗮𝗻𝘀", callback_data="style+sans", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("𝙎𝙖𝙣𝙨", callback_data="style+slant_sans", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("𝘚𝘢𝘯𝘴", callback_data="style+slant", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("𝖲𝖺𝗇𝗌", callback_data="style+sim", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("Ⓒ︎Ⓘ︎Ⓡ︎Ⓒ︎Ⓛ︎Ⓔ︎Ⓢ︎", callback_data="style+circles", style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton("🅒︎🅘︎🅡︎🅒︎🅛︎🅔︎🅢︎", callback_data="style+circle_dark", style=ButtonStyle.DANGER),
            InlineKeyboardButton("𝔊𝔬𝔱𝔥𝔦𝔠", callback_data="style+gothic", style=ButtonStyle.DANGER),
            InlineKeyboardButton("𝕲𝖔𝖙𝖍𝖎𝔈", callback_data="style+gothic_bolt", style=ButtonStyle.DANGER),
        ],
        [
            InlineKeyboardButton("C͜͡l͜͡o͜͡u͜͡d͜͡s͜͡", callback_data="style+cloud", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("H̆̈ă̈p̆̈p̆̈y̆̈", callback_data="style+happy", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("S̑̈ȃ̈d̑̈", callback_data="style+sad", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close_reply", style=ButtonStyle.DANGER),
            InlineKeyboardButton("ɴᴇxᴛ ➻", callback_data="nxt", style=ButtonStyle.SUCCESS),
        ],
    ]


def second_page_buttons():
    return [
        [
            InlineKeyboardButton("🇸 🇵 🇪 🇨 🇮 🇦 🇱 ", callback_data="style+special", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("🅂🅀🅄🄰🅁🄴🅂", callback_data="style+squares", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("🆂︎🆀︎🆄︎🅰︎🆁︎🅴︎🆂︎", callback_data="style+squares_bold", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("ꪖꪀᦔꪖꪶꪊᥴ𝓲ꪖ", callback_data="style+andalucia", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("爪卂几ᘜ卂", callback_data="style+manga", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("S̾t̾i̾n̾k̾y̾", callback_data="style+stinky", style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton("B̥ͦu̥ͦb̥ͦb̥ͦl̥ͦe̥ͦs̥ͦ", callback_data="style+bubbles", style=ButtonStyle.DANGER),
            InlineKeyboardButton("U͟n͟d͟e͟r͟l͟i͟n͟e͟", callback_data="style+underline", style=ButtonStyle.DANGER),
            InlineKeyboardButton("꒒ꍏꀷꌩꌃꀎꁅ", callback_data="style+ladybug", style=ButtonStyle.DANGER),
        ],
        [
            InlineKeyboardButton("R҉a҉y҉s҉", callback_data="style+rays", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("B҈i҈r҈d҈s҉", callback_data="style+birds", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("S̸l̸a̸s̸h̸", callback_data="style+slash", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton("s⃠t⃠o⃠p⃠", callback_data="style+stop", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("S̺͆k̺͆y̺͆l̺͆i̺͆n̺͆e̺͆", callback_data="style+skyline", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("A͎r͎r͎o͎w͎s͎", callback_data="style+arrows", style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton("ዪሀክቿነ", callback_data="style+qvnes", style=ButtonStyle.DANGER),
            InlineKeyboardButton("S̶t̶r̶i̶k̶e̶", callback_data="style+strike", style=ButtonStyle.DANGER),
            InlineKeyboardButton("F༙r༙o༙z༙e༙n༙", callback_data="style+frozen", style=ButtonStyle.DANGER),
        ],
        [
            InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close_reply", style=ButtonStyle.DANGER),
            InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="nxt+0", style=ButtonStyle.SUCCESS),
        ],
    ]


STYLES = {
    "typewriter": Fonts.typewriter,
    "outline": Fonts.outline,
    "serif": Fonts.serief,
    "bold_cool": Fonts.bold_cool,
    "cool": Fonts.cool,
    "small_cap": Fonts.smallcap,
    "script": Fonts.script,
    "script_bolt": Fonts.bold_script,
    "tiny": Fonts.tiny,
    "comic": Fonts.comic,
    "sans": Fonts.san,
    "slant_sans": Fonts.slant_san,
    "slant": Fonts.slant,
    "sim": Fonts.sim,
    "circles": Fonts.circles,
    "circle_dark": Fonts.dark_circle,
    "gothic": Fonts.gothic,
    "gothic_bolt": Fonts.bold_gothic,
    "cloud": Fonts.cloud,
    "happy": Fonts.happy,
    "sad": Fonts.sad,
    "special": Fonts.special,
    "squares": Fonts.square,
    "squares_bold": Fonts.dark_square,
    "andalucia": Fonts.andalucia,
    "manga": Fonts.manga,
    "stinky": Fonts.stinky,
    "bubbles": Fonts.bubbles,
    "underline": Fonts.underline,
    "ladybug": Fonts.ladybug,
    "rays": Fonts.rays,
    "birds": Fonts.birds,
    "slash": Fonts.slash,
    "stop": Fonts.stop,
    "skyline": Fonts.skyline,
    "arrows": Fonts.arrows,
    "qvnes": Fonts.rvnes,
    "strike": Fonts.strike,
    "frozen": Fonts.frozen,
}


@app.on_message(filters.command(["font", "fonts"]))
async def style_buttons(client, message):
    parts = (message.text or "").split(maxsplit=1)

    if len(parts) < 2 or not parts[1].strip():
        return await message.reply_text(
            "❌ Use: /font your text"
        )

    original_text = parts[1].strip()

    try:
        sent = await message.reply_text(
            original_text,
            reply_markup=InlineKeyboardMarkup(first_page_buttons()),
        )

        FONT_TEXTS[sent.id] = original_text

    except Exception:
        return await message.reply_text(
            "❌ Font message send nahi ho saka."
        )

    return sent


@app.on_callback_query(filters.regex(r"^nxt(?:\+0)?$"))
async def nxt(client, query):
    try:
        await query.answer()

        if query.data == "nxt":
            await query.message.edit_reply_markup(
                InlineKeyboardMarkup(second_page_buttons())
            )
        else:
            await query.message.edit_reply_markup(
                InlineKeyboardMarkup(first_page_buttons())
            )

    except Exception:
        try:
            await query.answer(
                "❌ Buttons update nahi ho sake.",
                show_alert=True,
            )
        except Exception:
            pass


@app.on_callback_query(filters.regex(r"^style\+"))
async def style(client, query):
    style_name = query.data.split("+", 1)[1]
    font_func = STYLES.get(style_name)

    if font_func is None:
        return await query.answer(
            "❌ Invalid font style.",
            show_alert=True,
        )

    await query.answer()

    message_id = query.message.id
    original_text = FONT_TEXTS.get(message_id)

    if not original_text:
        return await query.answer(
            "❌ Original text not found. Use /font again.",
            show_alert=True,
        )

    try:
        new_text = font_func(original_text)

        if not new_text:
            return await query.answer(
                "❌ Font returned empty text.",
                show_alert=True,
            )

        await query.message.edit_text(
            new_text,
            reply_markup=query.message.reply_markup,
        )

    except Exception:
        try:
            await query.answer(
                "❌ Font apply nahi ho saka.",
                show_alert=True,
            )
        except Exception:
            pass


@app.on_callback_query(filters.regex(r"^close_reply$"))
async def close_font(client, query):
    try:
        FONT_TEXTS.pop(query.message.id, None)
        await query.answer()
        await query.message.delete()

    except Exception:
        try:
            await query.answer(
                "❌ Message close nahi ho saka.",
                show_alert=True,
            )
        except Exception:
            pass


__help__ = """

❍ /fonts <text> *:* ᴄᴏɴᴠᴇʀᴛs sɪᴍᴩʟᴇ ᴛᴇxᴛ ᴛᴏ ʙᴇᴀᴜᴛɪғᴜʟ ᴛᴇxᴛ by ᴄʜᴀɴɢɪɴɢ ɪᴛ's ғᴏɴᴛ.
"""

__mod_name__ = "Fᴏɴᴛ"
