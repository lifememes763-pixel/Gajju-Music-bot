# -----------------------------------------------
# Helper utilities to show the YouTube thumbnail of the
# currently playing song in the "now playing" message,
# and to safely fall back to a plain text message if the
# photo can't be sent for any reason.
# -----------------------------------------------
from config import (
    SOUNCLOUD_IMG_URL,
    STREAM_IMG_URL,
    TELEGRAM_AUDIO_URL,
    TELEGRAM_VIDEO_URL,
)
from SHUKLAMUSIC.utils.thumbnails import get_thumb


async def now_playing_photo(videoid: str, kind: str = "youtube", is_video: bool = False) -> str:
    """
    Return the image to show as the "now playing" photo for the track that
    just started playing.

    kind:
      - "youtube"   -> the real YouTube thumbnail of the video (vidid required)
      - "telegram"  -> generic telegram audio/video cover
      - "soundcloud"-> generic soundcloud cover
      - "index"     -> generic stream cover (m3u8 / index links have no thumbnail)
    """
    if kind == "telegram":
        return TELEGRAM_VIDEO_URL if is_video else TELEGRAM_AUDIO_URL

    if kind == "soundcloud":
        return TELEGRAM_VIDEO_URL if is_video else SOUNCLOUD_IMG_URL

    if kind == "index":
        return STREAM_IMG_URL

    try:
        img = await get_thumb(videoid)
        return img or STREAM_IMG_URL
    except Exception:
        return STREAM_IMG_URL


async def send_now_playing(app, chat_id, photo, caption, reply_markup=None):
    """
    Send the "now playing" message with the song's photo (album art).
    Falls back to a plain text message if sending the photo fails.
    """
    try:
        return await app.send_photo(
            chat_id,
            photo=photo,
            caption=caption,
            reply_markup=reply_markup,
        )
    except Exception:
        return await app.send_message(
            chat_id,
            caption,
            reply_markup=reply_markup,
        )

