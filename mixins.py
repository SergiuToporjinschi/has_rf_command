from abc import abstractmethod
import logging

import RPi.GPIO as GPIO
from time import sleep

from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    BIT,
    CLOSE,
    COMMANDS,
    HIGH,
    INIT,
    LONG,
    LOW,
    OPEN,
    PAUSE,
    PIN,
    REPEAT,
    SHORT,
    STOP,
    TIME,
)

_LOGGER = logging.getLogger(__name__)

class GPIOCon(RestoreEntity):
    """GPIO connector"""
    _pin = -1
    _repeat = 3
    _pause = 8064
    _init_time_low = 2000
    _init_time_high = 5000
    _bit_time_short = 340
    _bit_time_long = 690
    _commands = {}

    def __init__(self, conf) -> None:
        _LOGGER.info("Rf_shades log ")
        self._pin = conf.get(PIN)
        self._repeat = conf.get(REPEAT)
        self._pause = conf.get(PAUSE)

        self._init_time_low = conf.get(INIT).get(TIME).get(LOW)
        self._init_time_high = conf.get(INIT).get(TIME).get(HIGH)
        self._bit_time_short = conf.get(BIT).get(TIME).get(SHORT)
        self._bit_time_long = conf.get(BIT).get(TIME).get(LONG)

        self._commands = conf.get(COMMANDS)
        self._convert_times_in_sec()

    def _convert_times_in_sec(self):
        self._pause = float(self._pause) / 1000000
        self._init_time_low = float(self._init_time_low) / 1000000
        self._init_time_high = float(self._init_time_high) / 1000000
        self._bit_time_short = float(self._bit_time_short) / 1000000
        self._bit_time_long  = float(self._bit_time_long) / 1000000

    def send_close(self):
        """Sends command to GPIO"""
        code = self._get_code() + " " + self._commands.get(CLOSE)
        _LOGGER.info("Send_close %s", code)
        self._send_code(code)

    def send_open(self):
        """Sends command to GPIO"""
        code = self._get_code() + " " + self._commands.get(OPEN)
        _LOGGER.info("Send_open %s", code)
        self._send_code(code)

    def send_stop(self):
        """Sends command to GPIO"""
        code = self._get_code() + " " + self._commands.get(STOP)
        _LOGGER.info("Send_stop %s", code)
        self._send_code(code)

    def _setup_gpio(self):
        """Initialize GPIO"""
        _LOGGER.info("Initialize GPIO")
        GPIO.setwarnings(False)
        # GPIO.setmode(GPIO.BOARD)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin, GPIO.OUT)
        sleep(0.05)

    @abstractmethod
    def _get_code(self)->str:
        pass

    def _send_code(self, command):
        """"Send code test"""
        command = command.replace(" ", "")
        _LOGGER.info("Sending code %s repeat: %s, initLow: %s, initHigh: %s, bitShort: %s, bitLong: %s",
            command, self._repeat, self._init_time_low, self._init_time_high, self._bit_time_short, self._bit_time_long)
        self._setup_gpio()
        for t in range(self._repeat):
            GPIO.output(self._pin, 1)
            sleep(self._init_time_high)
            GPIO.output(self._pin, 0)
            sleep(self._init_time_low)
            for i, k in enumerate(command):
                if (k == '1'):
                    GPIO.output(self._pin, 1)
                    sleep(self._bit_time_long)
                    GPIO.output(self._pin, 0)
                    sleep(self._bit_time_short)
                elif (k == '0'):
                    GPIO.output(self._pin, 1)
                    sleep(self._bit_time_short)
                    GPIO.output(self._pin, 0)
                    sleep(self._bit_time_long)
            sleep(self._pause)
