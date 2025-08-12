import os
import asyncio
import websockets
from urllib.parse import urlparse, parse_qs
import time
import json
import aio_pika
import logging
from asgiref.sync import sync_to_async

import django
django.setup()

from .models import Comment


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)



class WS:
    def __init__(self):
        self._host = os.getenv('RABBIT_HOST', '127.0.0.1')
        self._port = int(os.getenv('RABBIT_PORT', '5672'))
        self._user = os.getenv('RABBIT_USER', 'root')
        self._password = os.getenv('RABBIT_PASS', 'root1234')
        self._queue_name = os.getenv('RABBIT_QUEUE', 'comments_queue')
        self._connected_clients = {}
        self._logger = logging.getLogger(__name__)



    def _log(self, text):
        self._logger.error(f"{self.__class__.__name__}: {text}")




    async def broadcast(self, message):
        try:

            if self._connected_clients:
                await asyncio.gather(*[ws.send(message) for ws in self._connected_clients])
        
        except Exception as e:
            self._log(f"broadcast -> {e}")




    async def send_message_to_user(self, target_username, message):
        try:

            for ws, username in self._connected_clients.items():

                if username == target_username:
                    try:
                        await ws.send(message)
                        self._log(f"Сообщение отправлено пользователю {target_username}: {message}")

                    except websockets.exceptions.ConnectionClosed:
                        self._log(f"Не удалось отправить сообщение пользователю {target_username}, он отключился.")

                    break

        except Exception as e:
            self._log(f"send_message_to_user -> {e}")




    async def websocket_handler(self, websocket, path):
        query = urlparse(path).query
        params = parse_qs(query)
        username = params.get("username", ["Anonymous"])[0]
        self._connected_clients[websocket] = username

        test_obj_send = {
            "connected": "OK",
            "type": "WS"
        }

        await self.send_message_to_user(username, json.dumps(test_obj_send))
        
        try:
            async for message in websocket:
                self._log(f"{username} говорит: {message}")
                await self.broadcast(f"{username}: {message}")

        except websockets.exceptions.ConnectionClosed:
            self._log(f"{username} отключился")

        finally:
            self._connected_clients.pop(websocket, None)




    async def main(self):
        server = await websockets.serve(self.websocket_handler, "0.0.0.0", 8001)
        consumer_task = asyncio.create_task(self.rabbit_listener_loop())
        await server.wait_closed()




    @sync_to_async
    def _find_comment_with_id(self, id):
        try:

            return Comment.objects.get(id=id)
        
        except Exception as e:
            self._log(f"_find_comment_with_id -> {e}")
            return None




    async def _analyze_message(self, data):
        try:
            
            web_user = data.get("user")
            ws_user = data.get("ws_user")
            comment = data.get("comment")
            file = data.get("file")
            filetype = data.get("filetype", "")
            answer_id = data.get("answer_id")
            parent = None if answer_id == 0 else await self._find_comment_with_id(answer_id)

        
            @sync_to_async
            def save_comment():
                try:

                    obj = Comment.objects.create(
                        user=web_user,
                        text=comment,
                        file_path=file,
                        filetype=filetype,
                        parent=parent
                    )

                    return obj

                except Exception as e:
                    self._log(f"[!] save_comment -> {e}")
                    return False
            

            add = await save_comment()

            data_to_send = {
                "id": add.id if add else 0,
                "answer_id": answer_id,
                "created_at": add.created_at.strftime("%d.%m.%Y %H:%M:%S") if add else "1970-01-01 00:00:00",
                "user": web_user or "",
                "comment": comment or "",
                "ws_user": ws_user or "",
                "file": file,
                "filetype": filetype,
                "status": "allow" if add else "deny"
            }

            await self.send_message_to_user(
                ws_user, 
                json.dumps(data_to_send)
            )


        except Exception as e:
            self._log(f"[!] _analyze_message -> {e}")




    async def rabbit_listener_loop(self):

        while True:
            try:

                connection = await aio_pika.connect_robust(f"amqp://{self._user}:{self._password}@{self._host}/")

                channel = await connection.channel()
                queue = await channel.declare_queue(self._queue_name, durable=True)

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            
                            try:

                                data = json.loads(message.body.decode())
                                await self._analyze_message(data)

                            except json.JSONDecodeError as e:
                                self._log(f"[!] Ошибка JSON: {e}")

                            except Exception as e:
                                self._log(f"[!] Ошибка обработки: {e}")

            except aio_pika.exceptions.AMQPConnectionError as e:
                self._log(f"[!] Потеря соединения: {e}. Переподключение через 1 секунду...")
                await asyncio.sleep(1)

            except Exception as e:
                self._log(f"[!] Ошибка общего характера: {e}")
                await asyncio.sleep(1)




ws = WS()
asyncio.run(ws.main())