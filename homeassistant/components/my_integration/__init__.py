"""The My Integration integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .coordinator import MyIntegrationDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

type MyIntegrationConfigEntry = ConfigEntry[MyIntegrationDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: MyIntegrationConfigEntry) -> bool:
    """Set up My Integration from a config entry."""
    coordinator = MyIntegrationDataUpdateCoordinator(
        hass,
        entry=entry,
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        # Note: not logging here since async_config_entry_first_refresh already
        # logs the underlying error. Raising ConfigEntryNotReady is sufficient
        # to surface the failure in the UI and trigger automatic retries.
        raise ConfigEntryNotReady(
            translation_domain="my_integration",
            translation_key="cannot_connect",
        ) from err

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    # Personal note: using entry.title here gives a friendlier log message
    # than just the entry_id (which is a UUID and hard to read at a glance).
    _LOGGER.debug(
        "My Integration setup complete for entry '%s' (%s)",
        entry.title,
        entry.entry_id,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: MyIntegrationConfigEntry) -> bool:
    """Unload a config entry."""
    # Personal note: log unload so it's easier to trace entry lifecycle in the logs.
    _LOGGER.debug(
        "Unloading My Integration entry '%s' (%s)",
        entry.title,
        entry.entry_id,
    )
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, entry: MyIntegrationConfigEntry) -> None:
    """Reload config entry when options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)
