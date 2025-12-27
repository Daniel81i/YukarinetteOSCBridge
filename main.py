import os
import asyncio
import json
import logging

from osc_handler import OSCHandler
from yukari_api import YukariAPI
from tray import TrayIcon

transport = None

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

log_level = logging.DEBUG if config.get("DEBUG", False) else logging.INFO
logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(message)s")

api = YukariAPI(config)


# ---------------------------
# OSC 受信コールバック
# ---------------------------
async def on_input(value):
    """
    受信値のルール例：
    0 → Mute OFF
    1 → Mute ON
    100〜199 → LangID (100 → ItemNo=1)
    """

    retcode = 1  # デフォルトは失敗

    try:
        v = int(value)

        # Mute
        if v in (0, 1):
            ok = await api.set_mute(v)
            retcode = 0 if ok else 1

        # LangID
        elif 100 <= v <= 199:
            item_no = v - 99
            ok = await api.set_langid(item_no)
            retcode = 0 if ok else 1

        else:
            logging.warning(f"Unknown OSC value: {v}")

    except Exception as e:
        logging.error(f"Error processing OSC input: {e}")

    # 結果を返す
    osc.send_retcode(retcode)


# ---------------------------
# メイン処理
# ---------------------------
async def main():
    global osc
    global transport

    tray = TrayIcon(on_exit=on_exit)  # Exit コールバックを渡す
    tray.start()

    osc = OSCHandler(config, on_input)
    transport = await osc.start_server()

    while True:
        await asyncio.sleep(1)


def on_exit():
    # OSC ポートを閉じる
    try:
        transport.close()
        logging.info("OSC port closed.")
    except:
        pass

    # アプリ終了
    os._exit(0)

if __name__ == "__main__":
    asyncio.run(main())
