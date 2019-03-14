import pika
import uuid


class ServiceBServer:
    def __init__(self):
        self.connection = pika.BlockingConnection()
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue="serviceB")

    def on_request(self, ch, method, props, body):
        body = body.decode()
        response = "It's from ServiceB"

        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id=props.correlation_id),
                         body=str(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_request, queue='serviceB')
        self.channel.start_consuming()


if __name__ == "__main__":
    server = ServiceBServer()
    server.run()
