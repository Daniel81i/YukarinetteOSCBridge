import asyncio
import logging
import json
import winreg
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

from tray import TrayIcon
from yukari_api import YukariAPI

# ==========================
# 設定読み込み
# ==========================
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

log_level = logging.DEBUG if config.get("DEBUG", False) else logging.INFO
logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(message)s")

# ==========================
# ゆかり API 初期化
# ==========================
api = YukariAPI(config)

# ==========================
# OSC クライアント（送信用）
# ==========================
osc_client = SimpleUDPClient("127.0.0.1", config["OSC_SEND_PORT"])

# ==========================
# OSC 受信ハンドラ
# ==========================
async def on_mute(address, *args):
    value = int(args[0])
    ok = await api.set_mute(value)
    osc_client.send_message(config["OSC_PATH_SEND_RETCODE"], 0 if ok else 1)

async def on_langid(address, *args):
    value = int(args[0])
    ok = await api.set_langid(value)
    osc_client.send_message(config["OSC_PATH_SEND_RETCODE"], 0 if ok else 1)

# ==========================
# OSC サーバー起動
# ==========================
async def start_osc():
    dispatcher = Dispatcher()
    dispatcher.map(config["OSC_PATH_MUTE"], on_mute)
    dispatcher.map(config["OSC_PATH_LANGID"], on_langid)

    server = AsyncIOOSCUDPServer(
        ("0.0.0.0", config["OSC_RECV_PORT"]),
        dispatcher,
        asyncio.get_event_loop()
    )
    transport, protocol = await server.create_serve_endpoint()
    return transport

# ==========================
# メイン処理
# ==========================
async def main():
    tray = TrayIcon()
    tray.start()

    await start_osc()

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
