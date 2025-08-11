import json
import pika
import os
from time import sleep
import logging



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)



class RMQ:
    def __init__(self):
        self._host = os.getenv('RabbitMQ_IP', '172.22.0.9')
        self._port = 5672
        self._user = "root"
        self._password = "root1234"
        self._queue_name = "comments_queue"
        self._credentials = None
        self._connection = None
        self._channel = None
        self._logger = logging.getLogger(__name__)
        self._connect()
        


    def _log(self, text):
        self._logger.error(text)
        

        
    def _connect(self):
        try:
            
            self._credentials = pika.PlainCredentials(self._user, self._password)
            
            connection_params = pika.ConnectionParameters(
                host=self._host,
                port=self._port,
                credentials=self._credentials
            )

            try:
                self._connection = pika.BlockingConnection(connection_params)
                self._channel = self._connection.channel()
                return True
            except Exception as e:
                self._log(f"Ошибка подключения к RabbitMQ -> {e}")
                return False
                
        except Exception as e:
            self._log(f"_connect -> {e}")
            return False
        
        
        
        
    def send(self, data):
        if not self._connection or self._connection.is_closed:
            self._log('Попытка подключения при отправке...')
            if not self._connect():
                self._log('Не удалось подключиться к RabbitMQ')
                return False

        try:
            
            message = json.dumps(data)
            self._channel.queue_declare(queue=self._queue_name, durable=True)
            
            self._channel.basic_publish(
                exchange='',
                routing_key=self._queue_name,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2
                )
            )
                
            return True
            
            
        except Exception as e:
            self._log(f"send -> {e}")
            return False
            
             
    def close(self):
        if self._connection and not self._connection.is_closed:
            self._connection.close()