import logging
from typing import Any, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_CODE, CONF_DEVICES, CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import *

_LOGGER = logging.getLogger(__name__)
COVER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_CODE): cv.string
    }
)

async def validate_command(code):
    """Validate command is binary"""
    _LOGGER.info("Validation ")
    for i, item in enumerate(code):
        if int(item) not in [1, 0]:
            raise ValueError

class ConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config or options flow for Dummy Garage."""

    data: Optional[dict[str, Any]]

    def __init__(self):
        self.data = {CONF_DEVICES:[]}

    async def async_step_user(self, user_input: Optional[dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        _LOGGER.info(" initialize first step")
        errors: dict[str, str] = {}
        if user_input is not None:
            user_input[CONF_CODE] = user_input[CONF_CODE].replace(" ", "")
            try:
                await validate_command(user_input[CONF_CODE])
            except ValueError:
                errors[CONF_CODE] = "binaryError"
            if not errors:
                # Input is valid, set data.
                rf_conf = self.hass.data[DOMAIN].copy()
                self.data = rf_conf | user_input.copy()
                # self.data[CONF_DEVICES].append(user_input.copy())
                return self.async_create_entry(title=self.data.get(CONF_NAME), data=self.data)
                # return self.async_create_entry(title="RfCover", data=self.data)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default="Shade1"): cv.string,
                    vol.Required(CONF_CODE, default="10000101 00110001 11111000 10110001"): cv.string
                }
            ), errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Option flow handler"""
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] = None) -> FlowResult:
        """Menu step"""
        return self.async_show_menu(step_id="menu", menu_options=["gpio", "commands", "rf_config"])

    async def async_step_commands(self, user_input: dict[str, Any] = None) -> FlowResult:
        """Configuration for setting binary commands"""
        if user_input is not None:
            self.config_entry.data.get(COMMANDS).update(self.config_entry.data[COMMANDS] | user_input)
            return self.async_create_entry(title=user_input.get(CONF_NAME), data=user_input)
        return self.async_show_form(
            step_id="commands",
            data_schema=vol.Schema({
                    vol.Required(OPEN, default = self.config_entry.data.get(COMMANDS).get(OPEN)): cv.string,
                    vol.Required(CLOSE, default = self.config_entry.data.get(COMMANDS).get(CLOSE)): cv.string,
                    vol.Required(STOP, default = self.config_entry.data.get(COMMANDS).get(STOP)): cv.string
                }),
            last_step=True
        )

    async def async_step_gpio(self, user_input: dict[str, Any] = None) -> FlowResult:
        """"Configuration for setting GPIO"""
        if user_input is not None:
            self.config_entry.data = self.config_entry.data | user_input
            return self.async_create_entry(title=user_input.get(CONF_NAME), data=user_input)

        return self.async_show_form(
            step_id="gpio",
            data_schema=vol.Schema({
                    vol.Required(CONF_NAME, default=self.config_entry.data.get(CONF_NAME)): cv.string,
                    vol.Required(CONF_CODE, default=self.config_entry.data.get(CONF_CODE)): cv.string,
                    vol.Required(PIN, default=self.config_entry.data.get(PIN)): cv.positive_int,
                    vol.Required(REPEAT, default=self.config_entry.data.get(REPEAT)): cv.positive_int,
                    vol.Required(PAUSE, default=self.config_entry.data.get(PAUSE)): cv.positive_int
                }),
            last_step=True
        )

    async def async_step_rf_config(self, user_input: dict[str, Any] = None) -> FlowResult:
        """Configuration for setting RF protocol"""
        if user_input is not None:
            self.config_entry.data[INIT][LEN] = user_input[f"{INIT}_{LEN}"]
            self.config_entry.data[INIT][TIME][HIGH] = user_input[f"{INIT}_{TIME}_{HIGH}"]
            self.config_entry.data[INIT][TIME][LOW] = user_input[f"{INIT}_{TIME}_{LOW}"]
            self.config_entry.data[BIT][TIME][SHORT] = user_input[f"{BIT}_{TIME}_{SHORT}"]
            self.config_entry.data[BIT][TIME][LONG] = user_input[f"{BIT}_{TIME}_{LONG}"]
            return self.async_create_entry(title=user_input.get(CONF_NAME), data=user_input)
        return self.async_show_form(
            step_id="rf_config",
            data_schema=vol.Schema({
                    vol.Required(f"{INIT}_{LEN}", default = self.config_entry.data.get(INIT).get(LEN)): cv.positive_int,
                    vol.Required(f"{INIT}_{TIME}_{HIGH}", default = self.config_entry.data.get(INIT).get(TIME).get(HIGH)): cv.positive_int,
                    vol.Required(f"{INIT}_{TIME}_{LOW}", default = self.config_entry.data.get(INIT).get(TIME).get(LOW)): cv.positive_int,
                    vol.Required(f"{BIT}_{TIME}_{SHORT}", default = self.config_entry.data.get(BIT).get(TIME).get(SHORT)): cv.positive_int,
                    vol.Required(f"{BIT}_{TIME}_{LONG}", default = self.config_entry.data.get(BIT).get(TIME).get(LONG)): cv.positive_int,
                }),
            last_step=True
        )