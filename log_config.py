import logging

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

formatter =  logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

file_handler= logging.FileHandler('player.log')

file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# logging.basicConfig(filename='server.log',level = logging.INFO, format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s')

enable_tracing = False
enable_error= True
enable_info= True


# logger.info('create server:host {}, port {}, socket {}'.format(self._host,self._port, self._sock))
def trace(func):
    if enable_tracing:
        def callf(*args,**kwargs):
            logger.info("CALL %s: %s, %s\n" % (func.__name__, args, kwargs))
            r = func(*args,**kwargs)
            logger.info("%s RETURN %s\n" % (func.__name__, r))
            return r
        return callf
    else:
        return func
def log_error(error_f):
    if enable_error:
        logger.error(error_f)
    else:
        pass
    
def log_info(message):

    if enable_info:
        logger.info(message)
    else:
        pass

    