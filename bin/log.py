"""
log.py is defining a logging class for create log
"""
import logging

class log():
        def __init__(self, name):
            """
            initialize the log class
            """
            # configure logging
            logging.basicConfig(
                level=logging.INFO, 
                format='%(asctime)s - %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S - %Z',
                filename="log.txt",
                filemode='a'
                )
            self.name = name

        # set mode for logging
        def info(self, message: str, name = None):
            """
            do logging info
            
            
            :param message: the logging message
            :type message: str
            :param name: the entity name for logging
            :type name: str
            """
            if name is None:
                name = self.name
            self.logger = logging.getLogger(name)
            self.logger.info(message)

        def warn(self, message: str, name = None):
            """
            do logging warning
            
            :param message: the logging message
            :type message: str
            :param name: the entity name for logging
            :type name: str
            """
            if name is None:
                name = self.name
            self.logger = logging.getLogger(name)
            self.logger.warning(message)

        def error(self, message: str, name = None):
            """
            do logging error
            
            :param message: the logging message
            :type message: str
            :param name: the entity name for logging
            :type name: str
            """
            if name is None:
                name = self.name
            self.logger = logging.getLogger(name)
            self.logger.error(message)

        def debug(self, message: str, name = None):
            """
            do logging debug
            
            :param message: the logging message
            :type message: str
            :param name: the entity name for logging
            :type name: str
            """
            if name is None:
                name = self.name
            self.logger = logging.getLogger(name)
            
            self.logger.debug(message)

        def critical(self, message: str, name = None):
            """
            do logging critical
            
            :param message: the logging message
            :type message: str
            :param name: the entity name for logging
            :type name: str
            """
            if name is None:
                name = self.name
            self.logger = logging.getLogger(name)
            self.logger.critical(message)
        