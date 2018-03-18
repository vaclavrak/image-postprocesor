
from  carve.storages.BaseStorage import BasicStorage
import pika
import urllib.parse


class archive_rabbitmq(BasicStorage):

    def store(self):
        self.config.set_context('archive-id',  self.config.get_kv("{}/archive_id".format(self.m)))
        self.config.set_context('fileName', self.config.context.get(
                "storage_file_name", self.config.get_kv("{}/broken_image".format(self.m), "")))
        self.config.set_context('resolution', "{width}x{height}".format(**self.config.context))

        cacert = self.config.get_kv("{}/cacert".format(self.m))
        cert = self.config.get_kv("{}/cert".format(self.m))
        key = self.config.get_kv("{}/key".format(self.m))
        heartbeat = self.config.get_kv("{}/heartbeat".format(self.m))
        socket_timeout = self.config.get_kv("{}/socket_timeout".format(self.m), 30)
        exchange = self.config.get_kv("{}/exchange".format(self.m))
        routing_key = self.config.get_kv("{}/routing_key".format(self.m), "")
        uri = self.config.get_kv("{}/uri".format(self.m))

        params = urllib.parse.urlencode({
            'ssl_options': {'ca_certs':cacert, 'certfile': cert, 'keyfile': key, },
            'heartbeat': heartbeat,
            'socket_timeout': socket_timeout
        })
        full_uri = uri + "?" + params

        conn = pika.URLParameters(full_uri)
        connection = pika.BlockingConnection(conn)
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type='topic')
        channel.basic_publish(exchange=exchange, routing_key=routing_key, body="{}".format(self.config.context))

        connection.close()





