import json

from kafka import KafkaProducer
from kafka.errors import KafkaError


class ProducerMessanger:
    broker = ''
    topic = ''
    producer = None

    def __init__(
        self,
        broker: str,
        topic: str
    ):
        self.broker = broker
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=self.broker,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=3
            )

    def send_msg(self, msg_payload) -> None:
        try:
            future = self.producer.send(self.topic, msg_payload)
            future.get(timeout=60)
        except KafkaError as ex:
            print(ex)
