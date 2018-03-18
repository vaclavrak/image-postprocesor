import urllib.parse
from carve.sources.Source import BaseSource, BaseSourceException, logger
import pika
import time
from io import BytesIO
from PIL import Image
from carve.machinery.BaseImage import BaseImage


class ReadRmqMessagesException(Exception):
    pass


class ReadRmqMessages(object):
    _channels = None
    _ttl = None
    _queue = None
    _iproc = None
    _exchange = None
    _routing_key = None
    _connection = None

    def __init__(self):
        self._channel = None
        self._ttl = None
        self._queue = None
        self._durable = True
        self._iproc = None
        self._exchange = None
        self._routing_key = None
        self._connection = None

    def connect(self, uri):
        conn = pika.URLParameters(uri)
        self._connection = pika.BlockingConnection(conn)
        self._channel = self._connection.channel()
        return self

    @property
    def base_image(self):
        if self._bi is None:
            self._bi = BaseImage()
        return self._bi

    @property
    def connection(self):
        return self._connection

    @property
    def ch(self):
        if self._channel is None:
            raise ReadRmqMessages("Not connected to server, call connect first.")
        return self._channel

    @property
    def q(self):
        if self._queue is None:
            raise ReadRmqMessages("No queue specified.")
        return self._queue

    def ttl(self, ttl):
        self._ttl = ttl
        return self

    @property
    def ex(self):
        if self._exchange is None:
            raise ReadRmqMessages("No exchange specified.")
        return self._exchange

    @property
    def rk(self):
        if self._routing_key is None:
            raise ReadRmqMessages("No routing_key specified.")
        return self._routing_key

    def queue(self, queue):
        self._queue = queue
        return self

    def routing_key(self, rk):
        self._routing_key= rk
        return self

    def exchange(self, ex):
        self._exchange = ex
        return self

    def message_processor(self, iproc):
        self._iproc = iproc
        return self

    def durable(self, durable):
        if durable not in [True, False]:
            raise ReadRmqMessages("Durable have to be bool value.")
        self._durable = durable
        return self

    def consume(self, callback):
        args = {}

        if self._ttl is not None:
            args['x-message-ttl'] = self._ttl
        try:
            self.ch.queue_declare(queue=self.q, durable=self._durable, arguments=args)
            self.ch.queue_bind(queue=self.q, exchange=self.ex, routing_key=self.rk)
            self.ch.basic_qos(prefetch_count=1)
            self.ch.basic_consume(callback, queue=self.q, no_ack=False)
            self.ch.start_consuming()
        except Exception as e:
            print(e)


class rabbitmq(BaseSource):
    _rrm = None
    start_time = None

    def __init__(self):
        super(rabbitmq, self).__init__()
        self._rrm = None
        self.start_time = None

    @property
    def cacert(self):
        cacert = self._config._yml.get('source', {}).get('rabbitmq', {}).get('cacert', None)
        if cacert is None:
            raise BaseSourceException("No CaCert specified 'source/rabbitmq/cacert'")
        return cacert

    @property
    def key(self):
        key = self._config._yml.get('source', {}).get('rabbitmq', {}).get('key', None)
        if key is None:
            raise BaseSourceException("No Key specified 'source/rabbitmq/key'")
        return key


    @property
    def uri(self):
        uri = self._config._yml.get('source', {}).get('rabbitmq', {}).get('uri', None)
        if uri is None:
            raise BaseSourceException("No URI specified 'source/rabbitmq/uri'")
        return uri

    @property
    def exchange(self):
        ex = self._config._yml.get('source', {}).get('rabbitmq', {}).get('exchange', None)
        if ex is None:
            raise BaseSourceException("No Exchange specified 'source/rabbitmq/exchange'")
        return ex

    @property
    def routing_key(self):
        rk = self._config._yml.get('source', {}).get('rabbitmq', {}).get('bind', None)
        if rk is None:
            raise BaseSourceException("No `Bind` (routing key) specified 'source/rabbitmq/bind'")
        return rk

    @property
    def cert(self):
        cert = self._config._yml.get('source', {}).get('rabbitmq', {}).get('cert', None)
        if cert is None:
            raise BaseSourceException("No Cert specified 'source/rabbitmq/cert'")
        return cert

    @property
    def queue(self):
        queue = self._config._yml.get('source', {}).get('rabbitmq', {}).get('queue', None)
        if queue is None:
            raise BaseSourceException("No queue specified 'source/rabbitmq/queue'")
        return queue

    @property
    def ttl(self):
        ttl = self._config._yml.get('source', {}).get('rabbitmq', {}).get('message_ttl', None)
        return ttl

    @property
    def heartbeat(self):
        heartbeat = self._config._yml.get('source', {}).get('rabbitmq', {}).get('heartbeat', 30)
        return heartbeat

    @property
    def socket_timeout(self):
        socket_timeout = self._config._yml.get('source', {}).get('rabbitmq', {}).get('socket_timeout', 60)
        return socket_timeout

    @property
    def is_closed(self):
        if self.start_time is None:
            return True

        # time out for connecting
        if time.time() - self.start_time < 20:
            return False

        if not self._rrm:
            return True

        if not self._rrm.connection:
            return True

        return self._rrm.connection.is_closed

    def process_message(self, ch, method, properties, body):
        logger.info(properties)
        try:
            img = BytesIO(body)
            self.base_image.load_image(Image.open(img))
            self.base_image.set_time(properties.timestamp)
            self.config.make_context()
            self.work_with_image()
            ch.basic_ack(method.delivery_tag)
        except Exception as e:
            logger.error(e)
            ch.basic_ack(method.delivery_tag) # possibly not?

    def start(self):
        self.start_time = time.time()

        # print(self._config._yml)
        params = urllib.parse.urlencode({
            'ssl_options': {'ca_certs':self.cacert, 'certfile': self.cert, 'keyfile': self.key, },
            'heartbeat': self.heartbeat,
            'socket_timeout': self.socket_timeout
        })
        uri = self.uri + "?" + params
        logger.debug(uri)
        self._rrm = ReadRmqMessages().connect(uri)
        self._rrm.exchange(self.exchange)
        self._rrm.routing_key(self.routing_key)
        self._rrm.queue(self.queue)
        if self.ttl:
            self._rrm.ttl(self.ttl)
        self._rrm.consume(self.process_message)
        return self

    def stop(self):

        if not self.is_closed:
            if self._rrm:
                self._rrm.ch.stop_consuming()
                self._rrm.ch.close()
        self.start_time = None
        logger.info("Connection closed")
        return self



