from seleniumbase import Driver
from abc import ABC, abstractmethod
from enum import Enum
import logging
import os


class BotState(Enum):
    READY = 1
    RUNNING = 2
    STOPPED = 3


class Bot(ABC):

    def __init__(self):
        self.__driver = None
        self.__state = BotState.READY
        self.__options: dict = {"binary_location": os.getenv("SB_BINARY_LOCATION")}

    @property
    def driver(self):
        return self.__driver

    @property
    def state(self):
        return self.__state

    @abstractmethod
    def _setup(self): ...

    @abstractmethod
    def _teardown(self): ...

    @abstractmethod
    def _start(self):
        raise NotImplementedError("O método _start deve ser implementado.")

    def start(self):
        if self.__state == BotState.READY:
            try:
                binary_location = self.__options["binary_location"]
                self.__driver = Driver(uc=True, binary_location=binary_location)
                if self.__driver is None:
                    raise Exception("O driver não pôde ser inicializado.")
                self.__state = BotState.RUNNING
                self._setup()
                self._start()
                self._teardown()
            except Exception as err:
                logging.error(err)
            else:
                logging.info(f"Bot executado com sucesso!")
            finally:
                self.stop()

    def stop(self):
        if self.__driver is not None:
            logging.info(f"Finalizando a execução do bot.")
            self.__driver.quit()

    def reset(self):
        self.__driver = None
        self.__state = BotState.READY
