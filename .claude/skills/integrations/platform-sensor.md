# Sensor Platform Skill

This skill describes how to implement a sensor platform for a Home Assistant integration.

## File Location

`homeassistant/components/<integration>/sensor.py`

## Basic Structure

```python
"""Support for <Integration Name> sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MyIntegrationDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class MyIntegrationSensorEntityDescription(SensorEntityDescription):
    """Describes a sensor entity for MyIntegration."""

    value_fn: Callable[[dict[str, Any]], float | int | str | None]


SENSOR_DESCRIPTIONS: tuple[MyIntegrationSensorEntityDescription, ...] = (
    MyIntegrationSensorEntityDescription(
        key="temperature",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda data: data.get("temperature"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MyIntegration sensors based on a config entry."""
    coordinator: MyIntegrationDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        MyIntegrationSensorEntity(coordinator=coordinator, description=description)
        for description in SENSOR_DESCRIPTIONS
    )


class MyIntegrationSensorEntity(
    CoordinatorEntity[MyIntegrationDataUpdateCoordinator], SensorEntity
):
    """Representation of a MyIntegration sensor."""

    _attr_has_entity_name = True
    entity_description: MyIntegrationSensorEntityDescription

    def __init__(
        self,
        coordinator: MyIntegrationDataUpdateCoordinator,
        description: MyIntegrationSensorEntityDescription,
    ) -> None:
        """Initialize the sensor entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> float | int | str | None:
        """Return the current sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)
```

## Key Points

- Use `SensorEntityDescription` (or a subclass) to define sensor metadata declaratively.
- Always set `_attr_has_entity_name = True` and provide `translation_key` for entity naming.
- Use `CoordinatorEntity` to leverage a `DataUpdateCoordinator` for polling.
- Set `_attr_unique_id` using the config entry ID combined with the sensor key.
- Provide `device_info` from the coordinator so entities are grouped under a device.
- Use `SensorStateClass.MEASUREMENT` for continuously changing values, `TOTAL_INCREASING` for monotonically increasing totals.
- Prefer `native_unit_of_measurement` over `unit_of_measurement`; HA handles unit conversion automatically.
- The `value_fn` pattern keeps entity logic clean and testable.
