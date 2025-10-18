"""Config flow for Tian Realtime integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_OIL_PROVINCE,
    CONF_AIR_CITY,
    CONF_SCROLL_INTERVAL,
    DEFAULT_SCROLL_INTERVAL,
    MIN_SCROLL_INTERVAL,
    MAX_SCROLL_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

# 省份列表
PROVINCES = [
    "北京", "天津", "河北", "山西", "内蒙古", "辽宁", "吉林", "黑龙江",
    "上海", "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南",
    "湖北", "湖南", "广东", "广西", "海南", "重庆", "四川", "贵州",
    "云南", "西藏", "陕西", "甘肃", "青海", "宁夏", "新疆"
]

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    # 这里可以添加API验证逻辑
    return {"title": "天聚数行-实时动态"}

class TianRealtimeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tian Realtime."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        data_schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
            vol.Required(CONF_OIL_PROVINCE, default="福建"): vol.In(PROVINCES),
            vol.Required(CONF_AIR_CITY, default="莆田"): str,
            vol.Required(
                CONF_SCROLL_INTERVAL,
                default=DEFAULT_SCROLL_INTERVAL
            ): vol.All(
                vol.Coerce(int),
                vol.Range(min=MIN_SCROLL_INTERVAL, max=MAX_SCROLL_INTERVAL)
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "api_url": "https://www.tianapi.com/",
                "min_scroll": str(MIN_SCROLL_INTERVAL),
                "max_scroll": str(MAX_SCROLL_INTERVAL),
            }
        )