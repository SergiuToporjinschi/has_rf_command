import asyncio
import logging

import voluptuous as vol

from homeassistant import config_entries, core
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import *

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(PIN): cv.positive_int,
                vol.Required(REPEAT): cv.positive_int,
                vol.Required(PAUSE): cv.positive_int,
                vol.Required(COMMANDS): vol.Schema(
                    {
                        vol.Required(OPEN): cv.string,
                        vol.Required(CLOSE): cv.string,
                        vol.Required(STOP): cv.string
                    }
                ),
                vol.Required(INIT): vol.Schema(
                    {
                        vol.Required(LEN): cv.positive_int,
                        vol.Required(TIME): vol.Schema(
                            {
                                vol.Required(HIGH): cv.positive_int,
                                vol.Required(LOW): cv.positive_int,
                            }
                        ),
                    }
                ),
                vol.Required(BIT): vol.Schema(
                    {
                        vol.Required(TIME): vol.Schema(
                            {
                                vol.Required(SHORT): cv.positive_int,
                                vol.Required(LONG): cv.positive_int,
                            }
                        )
                    }
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Forward configuration to platform"""
    _LOGGER.info("Add")
    hass.data.setdefault(DOMAIN, {})
    config_entry.async_on_unload(config_entry.add_update_listener(options_update_listener))
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(config_entry, "cover")
    )
    return True



async def async_setup(hass: core.HomeAssistant, config: config_entries.ConfigEntry) -> bool:
    """Set up the RFCover component."""
    _LOGGER.info("Initializing %s", SERVICE_NAME)
    hass.data.setdefault(DOMAIN, config[DOMAIN])
    # hass.data[DOMAIN].update({CONF_DEVICES:[]})
    # hass.states.async_set(SERVICE_STATE_NAME, "False")
    # # hass.config_entries.async_update_entry(config, unique_id="sss")
    # async def async_handle_send_command(call):
    #     """handle send command service"""
    #     command = call.data.get(SERVICE_PAYLOAD_NAME, None)
    #     ## TODO add send command
    #     hass.states.async_set(SERVICE_STATE_NAME, "True")
    #     _LOGGER.info("Sending command %s", command)
    #     hass.states.async_set(SERVICE_STATE_NAME, "False")

    # hass.services.async_register(DOMAIN, SERVICE_NAME, async_handle_send_command)
    return True

async def options_update_listener(hass: core.HomeAssistant, config_entry: config_entries.ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass: core.HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[hass.config_entries.async_forward_entry_unload(entry, "cover")]
        )
    )
    return unload_ok
