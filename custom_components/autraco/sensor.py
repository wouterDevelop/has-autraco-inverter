"""Support for Autarco sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    PERCENTAGE,
    STATE_UNAVAILABLE,
    UnitOfPower,
    UnitOfEnergy
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AutarcoDataUpdateCoordinator


@dataclass
class AutarcoSensorEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable


@dataclass
class AutarcoSensorEntityDescription(
    SensorEntityDescription, AutarcoSensorEntityDescriptionMixin
):
    """Sensor entity description."""


SENSORS_ACCOUNT: tuple[AutarcoSensorEntityDescription, ...] = (
    AutarcoSensorEntityDescription(
        key="name",
        name="Name",
        value_fn=lambda data: data.account.name,
    ),
    AutarcoSensorEntityDescription(
        key="city",
        name="City",
        value_fn=lambda data: data.account.city,
    ),
    AutarcoSensorEntityDescription(
        key="timezone",
        name="Timezone",
        value_fn=lambda data: data.account.timezone,
    ),
)

SENSORS_INVERTER: tuple[AutarcoSensorEntityDescription, ...] = (
    AutarcoSensorEntityDescription(
        key="serial_number",
        name="Serial number",
        value_fn=lambda data: data.inverters.values(),
    ),
    AutarcoSensorEntityDescription(
        key="out_ac_power",
        name="AC output power",
        value_fn=lambda data: data.inverters.values(),
    ),
)

SENSORS_SOLAR: tuple[AutarcoSensorEntityDescription, ...] = (
    AutarcoSensorEntityDescription(
        key="power_production",
        name="Power Production",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        value_fn=lambda data: data.solar.power_production,
    ),
    AutarcoSensorEntityDescription(
        key="energy_production_today",
        name="Energy Production - Today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        value_fn=lambda data: data.solar.energy_production_today,
    ),
    AutarcoSensorEntityDescription(
        key="energy_production_month",
        name="Energy Production - Month",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        value_fn=lambda data: data.solar.energy_production_month,
    ),
    AutarcoSensorEntityDescription(
        key="energy_production_total",
        name="Energy Production - Total",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        value_fn=lambda data: data.solar.energy_production_total,
        state_class=SensorStateClass.TOTAL,

    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Autarco sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[AutarcoSensorEntity] = []
    entities.extend(
        AutarcoSensorEntity(
            coordinator=coordinator,
            description=description,
            name="Solar",
            service="solar",
        )
        for description in SENSORS_SOLAR
    )
    print(hass.data[DOMAIN][entry.entry_id].data)
    async_add_entities(entities)


class AutarcoSensorEntity(
    CoordinatorEntity[AutarcoDataUpdateCoordinator], SensorEntity
):
    """Defines an Autarco sensor."""

    coordinator: AutarcoDataUpdateCoordinator
    entity_description: AutarcoSensorEntityDescription

    def __init__(
        self,
        *,
        coordinator: AutarcoDataUpdateCoordinator,
        description: AutarcoSensorEntityDescription,
        name: str,
        service: str,
    ) -> None:
        """Initialize Autarco sensor."""
        super().__init__(coordinator=coordinator)

        self.entity_description = description
        self.entity_id = f"{SENSOR_DOMAIN}.{service}_{description.key}"
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{service}_{description.key}"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{coordinator.config_entry.entry_id}_{service}")},
            entry_type=DeviceEntryType.SERVICE,
            manufacturer="Autarco",
            name=name,
        )

    @property
    def native_value(self) -> int | float | str:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)
