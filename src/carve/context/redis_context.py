
from  carve.context.BaseContext import BaseContext
import redis


class redis_context(BaseContext):
    _srv = None
    _key_prefix = ""
    def __init__(self):
        self._srv = None

    @property
    def server(self) -> redis.StrictRedis:
        if self._srv is None:
            host = self.config.get_kv("{}/host".format(self.m), "localhost")
            port = self.config.get_kv("{}/port".format(self.m), 6379)
            db = self.config.get_kv("{}/db".format(self.m), 0)
            self._srv = redis.StrictRedis(host=host, port=port, db=db)
        return self._srv

    def prepare_context(self) -> object:
        for d in self.config.get_kvs("{}/keys".format(self.m)):
            d_str = d.get("key", None)
            if d_str:
                key_prefix = self.config.get_kv("{}/key_prefix".format(self.m), "")

                redis_key = "{}{}".format(key_prefix , d_str)
                k = d.get("name")
                v = self.server.get(redis_key)
                v = d.get("default", None) if v is None else v.decode("utf-8")

                self.config.set_context(k, v)

