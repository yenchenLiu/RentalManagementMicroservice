import pika
import uuid


class ServiceAServer:
    def __init__(self):
        self.connection = pika.BlockingConnection()
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue="serviceA")

    def on_request(self, ch, method, props, body):
        body = body.decode()
        if body == "get_data":
            response = "It's from ServiceA"
        elif body == "get_data_from_serviceB":
            client = ServiceAClient()
            response = client.call()
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id=props.correlation_id),
                         body=str(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_request, queue='serviceA')
        self.channel.start_consuming()


class ServiceAClient:
    serviceB = "serviceB"

    def __init__(self):

        self.connection = pika.BlockingConnection()
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.serviceB)
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key=self.serviceB,
                                   properties=pika.BasicProperties(
                                         reply_to=self.callback_queue,
                                         correlation_id=self.corr_id,
                                         ),
                                   body="get_data")
        while self.response is None:
            self.connection.process_data_events()
        return self.response.decode()


if __name__ == "__main__":
    server = ServiceAServer()
    server.run()
