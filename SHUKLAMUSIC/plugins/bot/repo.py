from pyrogram import filters
from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from SHUKLAMUSIC import app
from config import BOT_USERNAME
from SHUKLAMUSIC.utils.errors import capture_err
import httpx

# ── emoji_2e47b_by_TgEmodziBot pack IDs ──
_E_STAR   = 6073519257637884127   # 🌟
_E_HEART  = 6071046056555058251   # ❤️
_E_SPARK  = 6073301180673430006   # ✨
_E_GLOW   = 6073456529640525999   # 🤩
_E_FLOWER = 6073145973440253945   # 🌸
_E_LOVE   = 6073518286975276048   # 💗
_E_RIBBON = 6070857967052263096   # 🎀
_E_ROSE   = 6073547170630341250   # 🌹
_E_RIGHT  = 6073261718513913664   # ➡️
_E_BOUQ   = 6073117703965511893   # 💐

def e(eid, fb):
    return f'<emoji id={eid}>{fb}</emoji>'

start_txt = (
    f"{e(_E_STAR,'🌟')} {e(_E_GLOW,'🤩')} <b>𝗥𝗮𝗽𝗶𝗱𝗼 ⟡ 𝙈𝙪𝙨𝙞𝙘 𝘽𝙤𝙩 | GAJJU</b> {e(_E_GLOW,'🤩')} {e(_E_STAR,'🌟')}\n\n"
    f"{e(_E_SPARK,'✨')} ʙᴀᴅᴀ ᴀᴀʏᴀ ʙᴏᴛ ᴋᴀ ʀᴇᴘᴏ ᴅᴇᴋʜɴᴇ,\n"
    f"{e(_E_LOVE,'💗')} ᴘᴀʜʟᴇ ᴀᴘɴɪ ʟɪɢᴇ ᴋᴀ ʀᴇᴘᴏ sᴜᴅʜᴀʀ ᴊᴀᴀᴋᴇ !\n\n"
    f"<pre>||{e(_E_RIGHT,'➡️')} ᴜᴩᴛɪᴍᴇ       :  𝟷ʜ:𝟹𝟺ᴍ:𝟻𝟺s\n"
    f"{e(_E_RIGHT,'➡️')} sᴛᴏʀᴀɢᴇ      :  𝟸𝟽.𝟺%\n"
    f"{e(_E_RIGHT,'➡️')} ᴄᴩᴜ ʟᴏᴀᴅ    :  𝟷𝟷.𝟸%\n"
    f"{e(_E_RIGHT,'➡️')} ʀᴀᴍ ᴜsᴇ     :  𝟷𝟽.𝟻%||</pre>\n\n"
    f"{e(_E_ROSE,'🌹')} ᴘᴏᴡєʀєᴅ ʙʏ» <a href=\"https://t.me/II_GAJJU_III\">Rapido ⌯</a>\n"
    f"{e(_E_BOUQ,'💐')} {e(_E_FLOWER,'🌸')} {e(_E_RIBBON,'🎀')} {e(_E_HEART,'❤️')}"
)


@app.on_message(filters.command("repo"))
async def start(_, msg):
    buttons = [
        [
            InlineKeyboardButton(
                text="˹ηєᴛᴡᴏʀᴋ˼",
                url="https://t.me/MusiczHub0",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text="˹ϻʏ ʜᴏϻє˼",
                url="https://t.me/+bYa9ELse6J00MGM1",
                style=ButtonStyle.SUCCESS,
            ),
        ],
        [
            InlineKeyboardButton(
                text="˹ ϻʏ ϻᴧsᴛєʀ ˼ 👑",
                url="https://t.me/II_GAJJU_III",
                style=ButtonStyle.DANGER,
            ),
        ],
    ]

    await msg.reply_photo(
        photo="https://i.ibb.co/hFdRLqtZ/IMG-20261005-144514-837.jpg",
        caption=start_txt,
        reply_markup=InlineKeyboardMarkup(buttons),
    )
