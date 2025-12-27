import asyncio
import logging
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient


class OSCHandler:
    def __init__(self, config, on_mute, on_langid):
        """
        config: config.json の dict
        on_mute: Mute 受信時のコールバック
        on_langid: LangID 受信時のコールバック
        """

        self.config = config
        self.on_mute = on_mute
        self.on_langid = on_langid

        # 送信用 OSC クライアント
        self.client = SimpleUDPClient("127.0.0.1", config["OSC_SEND_PORT"])

        # ステータス
        self.status = "INIT"

    # -------------------------------------------------------
    # 送信（Mute / LangID / RetCode）
    # -------------------------------------------------------
    def send_mute(self, value):
        self.client.send_message(self.config["OSC_PATH_SEND_MUTE"], value)

    def send_langid(self, value):
        self.client.send_message(self.config["OSC_PATH_SEND_LANGID"], value)

    def send_retcode(self, code):
        self.client.send_message(self.config["OSC_PATH_SEND_RETCODE"], code)

    # -------------------------------------------------------
    # 受信ハンドラ
    # -------------------------------------------------------
    async def _handle_mute(self, address, *args):
        value = int(args[0])
        logging.debug(f"OSC Recv Mute: {value}")
        await self.on_mute(value)

    async def _handle_langid(self, address, *args):
        value = int(args[0])
        logging.debug(f"OSC Recv LangID: {value}")
        await self.on_langid(value)

    # -------------------------------------------------------
    # OSC サーバー起動
    # -------------------------------------------------------
    async def start_server(self):
        dispatcher = Dispatcher()

        # 受信パスを config.json から設定
        dispatcher.map(self.config["OSC_PATH_MUTE"], self._handle_mute)
        dispatcher.map(self.config["OSC_PATH_LANGID"], self._handle_langid)

        ip = "0.0.0.0"
        port = self.config["OSC_RECV_PORT"]

        logging.info(f"Starting OSC server on {ip}:{port}")

        server = AsyncIOOSCUDPServer((ip, port), dispatcher, asyncio.get_event_loop())
        transport, protocol = await server.create_serve_endpoint()

        self.status = "RUNNING"
        return transport
