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

import os
import random
import asyncio
from datetime import datetime, timedelta

from telegraph import upload_file
from PIL import Image, ImageDraw
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from SHUKLAMUSIC import app
from SHUKLAMUSIC.mongo.couples_db import _get_image, get_couple


POLICE = [
    [
        InlineKeyboardButton(
            text="ѕυρρσят",
            url="https://t.me/ALISA_X_SUPPORT",
        ),
    ],
]


def dt():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M")
    return dt_string.split(" ")


def dt_tom():
    tomorrow_date = datetime.now() + timedelta(days=1)
    return tomorrow_date.strftime("%d/%m/%Y")


tomorrow = dt_tom()
today = dt()[0]


@app.on_message(filters.command("couples"))
async def ctest(_, message):

    cid = message.chat.id

    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(
            "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs."
        )

    msg = None
    output_file = f"test_{cid}.png"
    pfp1_file = "./downloads/couple_pfp1.png"
    pfp2_file = "./downloads/couple_pfp2.png"

    try:
        msg = await message.reply_text(
            "ɢᴇɴᴇʀᴀᴛɪɴɢ ᴄᴏᴜᴘʟᴇs ɪᴍᴀɢᴇ..."
        )

        # GET LIST OF USERS
        list_of_users = []

        async for member in app.get_chat_members(cid, limit=50):
            if member.user and not member.user.is_bot:
                list_of_users.append(member.user.id)

        # Need at least 2 users
        if len(list_of_users) < 2:
            return await msg.edit_text(
                "❌ ɴᴇᴇᴅ ᴀᴛ ʟᴇᴀsᴛ 2 ᴍᴇᴍʙᴇʀs ᴛᴏ sᴇʟᴇᴄᴛ ᴄᴏᴜᴘʟᴇs."
            )

        # Select two different users
        c1_id, c2_id = random.sample(list_of_users, 2)

        # Get user information
        user1 = await app.get_users(c1_id)
        user2 = await app.get_users(c2_id)

        N1 = user1.mention
        N2 = user2.mention

        # Get profile photos
        photo1 = (await app.get_chat(c1_id)).photo
        photo2 = (await app.get_chat(c2_id)).photo

        # Default image
        default_pfp = "SHUKLAMUSIC/assets/upic.png"

        # Download first profile photo
        try:
            if photo1:
                p1 = await app.download_media(
                    photo1.big_file_id,
                    file_name=pfp1_file,
                )
            else:
                p1 = default_pfp
        except Exception:
            p1 = default_pfp

        # Download second profile photo
        try:
            if photo2:
                p2 = await app.download_media(
                    photo2.big_file_id,
                    file_name=pfp2_file,
                )
            else:
                p2 = default_pfp
        except Exception:
            p2 = default_pfp

        # Open images
        img1 = Image.open(p1).convert("RGBA")
        img2 = Image.open(p2).convert("RGBA")
        img = Image.open(
            "SHUKLAMUSIC/assets/cppic.png"
        ).convert("RGBA")

        # Resize profile pictures
        img1 = img1.resize((437, 437))
        img2 = img2.resize((437, 437))

        # Circular mask for first image
        mask = Image.new("L", img1.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse(
            (0, 0, img1.size[0], img1.size[1]),
            fill=255,
        )
        img1.putalpha(mask)

        # Circular mask for second image
        mask1 = Image.new("L", img2.size, 0)
        draw = ImageDraw.Draw(mask1)
        draw.ellipse(
            (0, 0, img2.size[0], img2.size[1]),
            fill=255,
        )
        img2.putalpha(mask1)

        # Paste images
        img.paste(img1, (116, 160), img1)
        img.paste(img2, (789, 160), img2)

        # Save final image
        img.save(output_file, format="PNG")

        TXT = f"""
**ᴛᴏᴅᴀʏ's ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ :

{N1} + {N2} = 💚

ɴᴇxᴛ ᴄᴏᴜᴘʟᴇs ᴡɪʟʟ ʙᴇ sᴇʟᴇᴄᴛᴇᴅ ᴏɴ {tomorrow} !!**
"""

        # Send generated image
        await message.reply_photo(
            output_file,
            caption=TXT,
            reply_markup=InlineKeyboardMarkup(POLICE),
        )

        # Delete loading message
        if msg:
            await msg.delete()

        # Upload image without blocking async event loop
        try:
            uploaded = await asyncio.to_thread(
                upload_file,
                output_file,
            )

            for x in uploaded:
                img_url = "https://graph.org/" + x

                couple = {
                    "c1_id": c1_id,
                    "c2_id": c2_id,
                }

                # Uncomment if your DB functions are ready:
                # await save_couple(cid, today, couple, img_url)

        except Exception:
            pass

    except Exception as e:
        print(f"Couples Error: {e}")

        if msg:
            try:
                await msg.edit_text(
                    "❌ ғᴀɪʟᴇᴅ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴄᴏᴜᴘʟᴇs ɪᴍᴀɢᴇ."
                )
            except Exception:
                pass

    finally:
        # Cleanup generated/downloaded files
        for file_path in [
            pfp1_file,
            pfp2_file,
            output_file,
        ]:
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception:
                pass


__mod__ = "COUPLES"

__help__ = """
**» /couples** - Get Todays Couples Of The Group In Interactive View
"""
