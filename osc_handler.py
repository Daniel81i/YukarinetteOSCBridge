import asyncio
import logging
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient


class OSCHandler:
    def __init__(self, config, on_input):
        """
        on_input(value): 受信値を main.py に渡すコールバック
        """
        self.config = config
        self.on_input = on_input

        self.client = SimpleUDPClient("127.0.0.1", config["OSC_SEND_PORT"])

    # ---------------------------
    # OSC 送信
    # ---------------------------
    def send_mute(self, value):
        self.client.send_message(self.config["OSC_PATH_SEND_MUTE"], value)

    def send_langid(self, value):
        self.client.send_message(self.config["OSC_PATH_SEND_LANGID"], value)

    def send_retcode(self, code):
        self.client.send_message(self.config["OSC_PATH_SEND_RETCODE"], code)

    # ---------------------------
    # OSC 受信
    # ---------------------------
    async def _handle_input(self, address, *args):
        value = args[0]
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug(f"[OSC HANDLER] addr={address}, args={args}, value={value}")
        await self.on_input(value)

    async def start_server(self):
        dispatcher = Dispatcher()
        dispatcher.map(self.config["OSC_PATH_RECV"], self._handle_input)

        ip = "0.0.0.0"
        port = self.config["OSC_RECV_PORT"]

        logging.info(f"Starting OSC server on {ip}:{port}")

        server = AsyncIOOSCUDPServer((ip, port), dispatcher, asyncio.get_event_loop())
        transport, protocol = await server.create_serve_endpoint()
        return transport
