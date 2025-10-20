"""Sensor platform for Tian Realtime integration."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    ENTITY_HOT_NEWS,
    ENTITY_OIL_PRICE,
    ENTITY_EXCHANGE_RATE,
    ENTITY_AIR_QUALITY,
    ENTITY_SCROLL_CONTENT,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    
    entities = [
        TianHotNewsSensor(coordinator, entry),
        TianOilPriceSensor(coordinator, entry),
        TianExchangeRateSensor(coordinator, entry),
        TianAirQualitySensor(coordinator, entry),
        TianScrollContentSensor(coordinator, entry),
    ]
    
    async_add_entities(entities)


class TianBaseSensor(CoordinatorEntity, SensorEntity):
    """Base sensor for Tian Realtime."""

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="实时动态",
            manufacturer="天聚数行",
            model="实时数据",
        )


class TianHotNewsSensor(TianBaseSensor):
    """Representation of Hot News Sensor."""

    _attr_name = ENTITY_HOT_NEWS
    _attr_unique_id = f"{DOMAIN}_hot_news"
    _attr_icon = "mdi:newspaper-variant-multiple"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("last_update")

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        data = self.coordinator.data.get("today_hot", {})
        # 确保包含 update_time 属性
        attributes = dict(data)
        # 如果数据中没有 update_time，使用 last_update
        if "update_time" not in attributes:
            attributes["update_time"] = self.coordinator.data.get("last_update")
        return attributes


class TianOilPriceSensor(TianBaseSensor):
    """Representation of Oil Price Sensor."""

    _attr_name = ENTITY_OIL_PRICE
    _attr_unique_id = f"{DOMAIN}_oil_price"
    _attr_icon = "mdi:gas-station"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("last_update")

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        data = self.coordinator.data.get("today_oil", {})
        # 确保包含 update_time 属性
        attributes = dict(data)
        # 如果数据中没有 update_time，使用 last_update
        if "update_time" not in attributes:
            attributes["update_time"] = self.coordinator.data.get("last_update")
        return attributes


class TianExchangeRateSensor(TianBaseSensor):
    """Representation of Exchange Rate Sensor."""

    _attr_name = ENTITY_EXCHANGE_RATE
    _attr_unique_id = f"{DOMAIN}_exchange_rate"
    _attr_icon = "mdi:currency-usd"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("last_update")

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        data = self.coordinator.data.get("today_rate", {})
        # 确保包含 update_time 属性
        attributes = dict(data)
        # 如果数据中没有 update_time，使用 last_update
        if "update_time" not in attributes:
            attributes["update_time"] = self.coordinator.data.get("last_update")
        return attributes


class TianAirQualitySensor(TianBaseSensor):
    """Representation of Air Quality Sensor."""

    _attr_name = ENTITY_AIR_QUALITY
    _attr_unique_id = f"{DOMAIN}_air_quality"
    _attr_icon = "mdi:air-filter"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("last_update")

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        data = self.coordinator.data.get("today_air", {})
        # 确保包含 update_time 属性
        attributes = dict(data)
        # 如果数据中没有 update_time，使用 last_update
        if "update_time" not in attributes:
            attributes["update_time"] = self.coordinator.data.get("last_update")
        return attributes


class TianScrollContentSensor(TianBaseSensor):
    """Representation of Scroll Content Sensor."""

    _attr_name = ENTITY_SCROLL_CONTENT
    _attr_unique_id = f"{DOMAIN}_scroll_content"
    _attr_icon = "mdi:chart-box-outline"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("last_update")

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self.coordinator.get_scroll_data()