# -----------------------------------------------
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

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ButtonStyle
from SHUKLAMUSIC.utils.Shukla_font import Fonts
from SHUKLAMUSIC import app


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
            InlineKeyboardButton("B҈i҈r҈d҈s҈", callback_data="style+birds", style=ButtonStyle.PRIMARY),
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


@app.on_message(filters.command(["font", "fonts"]))
async def style_buttons(c, m, cb=False):
    if not cb:
        parts = (m.text or "").split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            return await m.reply_text(
                "❌ <b>Use:</b> <code>/font your text</code>",
                quote=True,
            )

        text = parts[1].strip()
        buttons = first_page_buttons()

        return await m.reply_text(
            f"`{text}`",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True,
        )

    await m.answer()
    await m.message.edit_reply_markup(
        InlineKeyboardMarkup(first_page_buttons())
    )


@app.on_callback_query(filters.regex(r"^nxt"))
async def nxt(c, m):
    if m.data == "nxt":
        await m.answer()
        await m.message.edit_reply_markup(
            InlineKeyboardMarkup(second_page_buttons())
        )
    elif m.data == "nxt+0":
        await m.answer()
        await m.message.edit_reply_markup(
            InlineKeyboardMarkup(first_page_buttons())
        )


@app.on_callback_query(filters.regex(r"^style\+"))
async def style(c, m):
    styles = {
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

    _, style_name = m.data.split("+", 1)
    cls = styles.get(style_name)

    if cls is None:
        return await m.answer("❌ Invalid font style.", show_alert=True)

    await m.answer()

    raw = m.message.text or m.message.caption or ""
    target_text = raw.strip().strip("`").strip()

    if not target_text:
        return await m.answer(
            "❌ Text not found.",
            show_alert=True,
        )

    try:
        new_text = cls(target_text)
        await m.message.edit_text(
            new_text,
            reply_markup=m.message.reply_markup,
        )
    except Exception:
        pass


__help__ = """

 ❍ /fonts <text> *:* ᴄᴏɴᴠᴇʀᴛs sɪᴍᴩʟᴇ ᴛᴇxᴛ ᴛᴏ ʙᴇᴀᴜᴛɪғᴜʟ ᴛᴇxᴛ by ᴄʜᴀɴɢɪɴɢ ɪᴛ's ғᴏɴᴛ.
 """

__mod_name__ = "Fᴏɴᴛ"
