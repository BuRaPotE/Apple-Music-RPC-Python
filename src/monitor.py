import asyncio
import io
import time

import json
import logging
import traceback
import websockets

from PIL import Image
import winsdk.windows.media.control as wmctrl
from winsdk.windows.storage.streams import IRandomAccessStreamReference, Buffer, InputStreamOptions

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

WEBSOCKET_URL = "ws://localhost:8765"

class MediaMonitor:
    def __init__(self):
        self.session_manager = None
        self.media_session = None
        self.event_loop = asyncio.get_event_loop()
        self.listened_at = time.time()

    async def setup(self):
        print("Monitor Loaded")
        logger.info("[INFO] Setting up the monitor...")
        self.session_manager = await wmctrl.GlobalSystemMediaTransportControlsSessionManager.request_async()
        self.session_manager.add_sessions_changed(self.on_sessions_changed)
        logger.info("[INFO] Session manager initialized!")

        if self.session_manager:
            session = await self.get_current_session()
            if session:
                logger.info("[INFO] Apple Music session found.")
                self.media_session = session
                logger.info("[INFO] Adding event handlers...")
                self.media_session.add_media_properties_changed(self.on_media_properties_changed)
                self.media_session.add_playback_info_changed(self.on_playback_info_changed)
                logger.info("[INFO] Event handlers added.")
                await self.monitor_session()

    async def get_current_session(self, max_retries=10000):
        for x in range(max_retries):
            sessions = self.session_manager.get_sessions()
            if not sessions:
                logger.info("[INFO] No sessions found.")
                self.media_session = None

            for session in sessions:
                if 'Apple' in session.source_app_user_model_id:
                    logger.info("[INFO] Apple Music session found")
                    self.media_session = session
                    break
                else:
                    logger.info("[INFO] Apple Music session not found.")
                    self.media_session = None
                    await asyncio.sleep(1 + 0.25*x)
            else:
                continue

            break

        return self.media_session

    async def monitor_session(self):
        logger.info("[INFO] Monitoring the session for changes...")
        while True:
            if self.media_session:
                playback_status = self.media_session.get_playback_info().playback_status # https://learn.microsoft.com/ja-jp/uwp/api/windows.media.control.globalsystemmediatransportcontrolssessionplaybackstatus?view=winrt-26100
                if playback_status == wmctrl.GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING:
                    timeline_properties = self.media_session.get_timeline_properties()
                #print(f"Position: {timeline_properties.position.total_seconds()} / {timeline_properties.end_time.total_seconds()} seconds")  # https://learn.microsoft.com/ja-jp/uwp/api/windows.media.control.globalsystemmediatransportcontrolssessiontimelineproperties?view=winrt-26100
            await asyncio.sleep(1)  # Adjust delay as needed

    def on_sessions_changed(self, sender, args):
        asyncio.run_coroutine_threadsafe(self.get_current_session(), self.event_loop)  # https://learn.microsoft.com/ja-jp/uwp/api/windows.media.control.globalsystemmediatransportcontrolssessionmanager.sessionschanged?view=winrt-26100#windows-media-control-globalsystemmediatransportcontrolssessionmanager-sessionschanged

    def on_playback_info_changed(self, sender, args):
        logger.debug("[DEBUG] Playback info changed.")
        asyncio.run_coroutine_threadsafe(self.handle_playback_info_changed(), self.event_loop)

    def on_media_properties_changed(self, sender, args):
        logger.debug("[DEBUG] Media properties changed.")
        asyncio.run_coroutine_threadsafe(self.handle_media_properties_changed(), self.event_loop)  # I'm not sure if this is the best way to do this

    async def handle_playback_info_changed(self):
        logger.debug("[DEBUG] Handling playback info changed.")

    async def save_thumbnail(self, thumbnail_ref: IRandomAccessStreamReference):
        stream = await thumbnail_ref.open_read_async()

        buffer = Buffer(stream.size)
        try:
            data = await stream.read_async(buffer, buffer.capacity, InputStreamOptions.READ_AHEAD)
        except Exception as e:
            logger.debug(f"[DEBUG] Error reading stream: {e}")
            traceback.print_exc()
            return

        try:
            image_data = io.BytesIO(data)
            image = Image.open(image_data)

            image.save("thumbnail.png")
            del buffer # Release buffer... will it be able to prevent tending to memory leak? idk :(
            logger.info("[INFO] Thumbnail saved as 'thumbnail.png'")
        except Exception as e:
            logger.debug(f"[DEBUG] Error saving thumbnail: {e}")


    async def handle_media_properties_changed(self):
        media_properties = await self.media_session.try_get_media_properties_async()
        logger.info(f"[INFO] Title: {media_properties.title}")
        logger.info(f"[INFO] Artist: {media_properties.album_artist}")

        async with websockets.connect(WEBSOCKET_URL) as websocket:
            data = {
                "title": media_properties.title,
                "artist": media_properties.artist,
                "album_name": media_properties.album_title,
                "status": self.media_session.get_playback_info().playback_status.value,
                "position": self.media_session.get_timeline_properties().position.total_seconds(),
                "end": self.media_session.get_timeline_properties().end_time.total_seconds(),
                "listened_at": self.listened_at,
            }
            await websocket.send(json.dumps(data))
            print("Data sent:", data)
            self.listened_at = int(time.time())

        if hasattr(media_properties, 'thumbnail') and media_properties.thumbnail:
            await self.save_thumbnail(media_properties.thumbnail)

async def start_monitor():
    monitor = MediaMonitor()
    await monitor.setup()

if __name__ == "__main__":
    asyncio.run(start_monitor())
