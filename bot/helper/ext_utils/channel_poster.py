"""
Channel poster: sends a formatted TMDB movie/show post to PopCorn private channel.
Handles: main post (with poster image + caption), and optionally a Telegram Story.
"""
import io
from logging import getLogger
from os import path as ospath

import aiohttp
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait, RPCError
from asyncio import sleep

LOGGER = getLogger(__name__)

POPCORN_CHANNEL_ID = -1003900139131


async def send_channel_post(client, tmdb_info: dict, file_msg, filename: str):
    """
    Send a formatted post to the PopCorn private channel after upload.
    :param client: Pyrogram client
    :param tmdb_info: dict with TMDB data
    :param file_msg: the uploaded Telegram message (video/document)
    :param filename: original filename
    """
    from .tmdb_utils import format_tmdb_caption, fetch_tmdb_poster

    caption = format_tmdb_caption(tmdb_info, filename)
    poster_url = tmdb_info.get("poster_url", "") if tmdb_info else ""

    try:
        if poster_url:
            # Download poster
            poster_bytes = await fetch_tmdb_poster(poster_url)
            if poster_bytes:
                poster_io = io.BytesIO(poster_bytes)
                poster_io.name = "poster.jpg"
                sent = await client.send_photo(
                    chat_id=POPCORN_CHANNEL_ID,
                    photo=poster_io,
                    caption=caption,
                    parse_mode="html",
                )
                LOGGER.info(f"Channel poster post sent: {sent.id}")
                return sent

        # Fallback: just send text post
        sent = await client.send_message(
            chat_id=POPCORN_CHANNEL_ID,
            text=caption,
            parse_mode="html",
            disable_web_page_preview=False,
        )
        LOGGER.info(f"Channel text post sent: {sent.id}")
        return sent

    except FloodWait as fw:
        LOGGER.warning(f"FloodWait {fw.value}s when posting to channel")
        await sleep(fw.value + 2)
    except RPCError as e:
        LOGGER.error(f"RPCError posting to channel: {e}")
    except Exception as e:
        LOGGER.error(f"Error posting to channel: {e}")
    return None


async def forward_video_to_channel(client, file_msg, caption: str = ""):
    """
    Forward/copy the uploaded video message to the PopCorn channel.
    :param client: Pyrogram client
    :param file_msg: the uploaded message
    :param caption: optional caption override
    """
    try:
        if file_msg is None:
            return None

        copied = await client.copy_message(
            chat_id=POPCORN_CHANNEL_ID,
            from_chat_id=file_msg.chat.id,
            message_id=file_msg.id,
            caption=caption or file_msg.caption,
            parse_mode="html",
        )
        LOGGER.info(f"Video forwarded to channel: {copied.id}")
        return copied
    except FloodWait as fw:
        LOGGER.warning(f"FloodWait {fw.value}s forwarding to channel")
        await sleep(fw.value + 2)
    except RPCError as e:
        LOGGER.error(f"RPCError forwarding to channel: {e}")
    except Exception as e:
        LOGGER.error(f"Error forwarding to channel: {e}")
    return None
