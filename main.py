import os
import asyncio
import json
import logging
import sys
import subprocess

from osc_handler import OSCHandler
from yukari_api import YukariAPI
from tray import TrayIcon

transport = None
main_loop = None
shutdown_event = asyncio.Event()
shutdown_lock = asyncio.Lock()
last_exit_reason = None

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

log_level = logging.DEBUG if config.get("DEBUG", False) else logging.INFO
logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(message)s")
logging.info("=== YukarinetteOSCBridge started ===")
logging.info(f"Python version: {sys.version.replace(os.linesep, ' ')}")

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
# プロセス監視
# ---------------------------
def is_process_running(process_name: str) -> bool:
    """Windows の tasklist を使ってプロセスの存在を確認する."""
    if not process_name:
        # 設定されていない場合は「常に動いている」扱いにして監視を無効化
        return True

    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {process_name}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return process_name.lower() in result.stdout.lower()
    except Exception as e:
        logging.error(f"Process check failed: {e}")
        # 監視側でアプリを落としすぎないよう、エラー時は True 扱い
        return True
async def process_watchdog():
    """TARGET_PROCESS を定期的に監視し、落ちていたらアプリを終了させる."""
    target = config.get("TARGET_PROCESS", "")
    interval = config.get("PROCESS_CHECK_INTERVAL_SEC", 5)

    if not target:
        logging.info("TARGET_PROCESS not configured. Process watchdog disabled.")
        return

    logging.info(f"Process watchdog enabled. TARGET_PROCESS={target}, interval={interval}s")

    while True:
        await asyncio.sleep(interval)

        if not is_process_running(target):
            logging.warning(f"Target process '{target}' not found. Requesting shutdown.")
            await shutdown("process_watchdog")
            break


# ---------------------------
# 終了処理
# ---------------------------
async def shutdown(reason: str):
    """
    アプリ終了要求を共通処理で受ける.
    reason:
      - "user_exit"          : タスクトレイからの終了
      - "process_watchdog"   : 監視中のプロセスが消えた
      - "keyboard_interrupt" : Ctrl+Cなど
      - "error"              : 何かのエラーによる終了
      など自由に文字列で指定
    """
    global transport, last_exit_reason

    async with shutdown_lock:
        if shutdown_event.is_set():
            # すでに終了中
            return

        last_exit_reason = reason
        logging.info(f"Shutdown requested. reason={reason}")

        # ★ 使用中の OSC ポートをクローズ（要件 2）
        if transport is not None:
            try:
                transport.close()
                logging.info("OSC port closed.")
            except Exception as e:
                logging.error(f"Error closing OSC port: {e}")

        # ★ 終了イベントをセット
        shutdown_event.set()


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
    """タスクトレイからの終了メニュー選択時に呼ばれる."""
    global main_loop
    logging.info("Tray exit requested.")

    # イベントループがまだ取れていない場合は即終了（念のため）
    if main_loop is None:
        logging.info("Event loop not ready. Exiting immediately.")
        os._exit(0)

    # 非同期の shutdown() をイベントループ側で実行
    def _schedule_shutdown():
        asyncio.create_task(shutdown("user_exit"))

    main_loop.call_soon_threadsafe(_schedule_shutdown)

if __name__ == "__main__":
    asyncio.run(main())
