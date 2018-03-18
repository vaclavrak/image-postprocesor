from django.core.management.base import BaseCommand, CommandError
from os import listdir
from os.path import isfile, join
from carve.Controller import Configurator
import threading
import time
from logging  import getLogger

logger = getLogger("core")


class Command(BaseCommand):
    help = 'start carver daemon'
    verb = 0
    daemons = []

    def info(self, m):
        if self.verb > 0:
            self.stdout.write(m)

    def error(self, m):
        if self.verb > 0:
            self.stdout.write(self.style.ERROR(m))

    def debug(self, m):
        if self.verb > 1:
            self.stdout.write(m)

    def add_arguments(self, parser):
        parser.add_argument('--dir', '-d', dest='dir',  default="/etc/webcam/carve.d/",
                            help='config folder default is /etc/webcam/carve.d/')

        parser.add_argument('--reconnect', '-r', dest='reconnect',  default=True,
                            help='automatic reconnection if data source connection is lost')

    def handle(self, *args, **options):
        self.verb = options['verbosity']
        conf_path = options['dir']
        reconnect = options['reconnect']
        try:
            self.debug(conf_path)
            for f in listdir(conf_path):
                if isfile(join(conf_path, f)):
                    self.debug("File {}/{}".format(conf_path, f))
                    config = Configurator().read("{}/{}".format(conf_path, f))
                    for s in config.sources:
                        t = threading.Thread(target=s.start)
                        t.__setattr__("source", s)
                        self.daemons.append(t)
                        t.start()
            s = None
            t = None

            while len(self.daemons) > 0:
                for t in self.daemons:
                    if not t.is_alive():
                        self.info("Removing dead daemon: {} ".format(t.source))
                        s = t.source
                        t.source.stop()
                        self.daemons.remove(t)
                        t = None
                        if reconnect:
                            self.info("Daemon reconnecting")
                            t = threading.Thread(target=s.start, daemon=True)
                            t.__setattr__("source", s)
                            self.daemons.append(t)
                            t.start()

                time.sleep(1)

        except Exception as e:
            logger.exception(e)
            raise CommandError(str(e))
        finally:
            while len(self.daemons) > 0:
                if t is None:
                    break
                if t.source:
                    t.source.stop()
                t.join()
                self.daemons.remove(t)
                t = None
        self.stdout.write(self.style.SUCCESS('Successfully closed'))
