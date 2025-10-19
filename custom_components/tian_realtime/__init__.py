"""The Tian Realtime integration."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import logging
import random

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util
from homeassistant.helpers.event import async_track_time_interval, async_track_utc_time_change

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_OIL_PROVINCE,
    CONF_AIR_CITY,
    CONF_SCROLL_INTERVAL,
    API_BASE_URL,
    API_HOT_NEWS,
    API_OIL_PRICE,
    API_EXCHANGE_RATE,
    API_AIR_QUALITY,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tian Realtime from a config entry."""
    
    # 创建会话
    session = aiohttp.ClientSession()
    
    coordinator = TianRealtimeCoordinator(
        hass,
        session,
        entry.data[CONF_API_KEY],
        entry.data[CONF_OIL_PROVINCE],
        entry.data[CONF_AIR_CITY],
        entry.data[CONF_SCROLL_INTERVAL]
    )
    
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "session": session
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        data = hass.data[DOMAIN].pop(entry.entry_id)
        coordinator = data["coordinator"]
        # 取消滚动更新和定时更新
        coordinator.cancel_all_updates()
        if "session" in data:
            await data["session"].close()

    return unload_ok


class TianRealtimeCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Tian Realtime data."""

    def __init__(self, hass, session, api_key, oil_province, air_city, scroll_interval):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            # 不再使用固定的更新间隔，改为定时触发
            update_interval=None,
        )
        
        self.session = session
        self.api_key = api_key
        self.oil_province = oil_province
        self.air_city = air_city
        self.scroll_interval = scroll_interval
        self._data_cache = {}
        self._hot_data = {}
        self._current_hot_index = 0
        self._scroll_update_unsub = None
        self._scheduled_update_unsub = []
        self._last_successful_update = None
        
        # 启动定时更新和滚动更新
        self._setup_scheduled_updates()
        self._setup_scroll_updates()

    def _setup_scheduled_updates(self):
        """Setup scheduled updates at 7:00 and 16:00."""
        # 取消现有的定时器
        self.cancel_scheduled_updates()
        
        # 获取当前时间
        now = dt_util.now()
        _LOGGER.info(f"Setting up scheduled updates. Current time: {now}")
        
        # 设置早上7点的定时更新
        self._scheduled_update_unsub.append(
            async_track_utc_time_change(
                self.hass,
                self._async_scheduled_update,
                hour=7,
                minute=0,
                second=0
            )
        )
        
        # 设置下午16点的定时更新
        self._scheduled_update_unsub.append(
            async_track_utc_time_change(
                self.hass,
                self._async_scheduled_update,
                hour=16,
                minute=0,
                second=0
            )
        )
        
        # 检查是否需要立即执行一次更新
        current_hour = now.hour
        if current_hour >= 7 and current_hour < 16:
            # 如果当前时间在7点之后、16点之前，且今天还没有更新过，则立即更新
            if not self._last_successful_update or dt_util.parse_datetime(self._last_successful_update).date() < now.date():
                _LOGGER.info("Current time between 7:00 and 16:00, performing initial update")
                self.hass.async_create_task(self._async_scheduled_update())
        elif current_hour >= 16:
            # 如果当前时间在16点之后，且今天还没有16点的更新，则立即更新
            if not self._last_successful_update or dt_util.parse_datetime(self._last_successful_update).date() < now.date() or (
                dt_util.parse_datetime(self._last_successful_update).hour < 16 and current_hour >= 16):
                _LOGGER.info("Current time after 16:00, performing initial update")
                self.hass.async_create_task(self._async_scheduled_update())
        
        _LOGGER.info("Scheduled updates set for 7:00 and 16:00 daily")

    def _setup_scroll_updates(self):
        """Setup periodic scroll updates."""
        # 取消现有的定时器
        self.cancel_scroll_updates()
        
        # 设置新的定时器
        self._scroll_update_unsub = async_track_time_interval(
            self.hass,
            self._async_update_scroll_content,
            timedelta(seconds=self.scroll_interval)
        )

    async def _async_scheduled_update(self, now=None):
        """Perform scheduled update at 7:00 and 16:00."""
        _LOGGER.info("Performing scheduled data update at %s", dt_util.now())
        await self.async_refresh()

    def cancel_scroll_updates(self):
        """Cancel scroll updates."""
        if self._scroll_update_unsub:
            self._scroll_update_unsub()
            self._scroll_update_unsub = None

    def cancel_scheduled_updates(self):
        """Cancel scheduled updates."""
        for unsub in self._scheduled_update_unsub:
            unsub()
        self._scheduled_update_unsub = []

    def cancel_all_updates(self):
        """Cancel all updates."""
        self.cancel_scroll_updates()
        self.cancel_scheduled_updates()

    @callback
    def _async_update_scroll_content(self, now=None):
        """Update scroll content without calling API."""
        if self._hot_data and len(self._hot_data) > 0:
            # 更新当前头条索引
            self._current_hot_index = (self._current_hot_index + 1) % len(self._hot_data)
            
            # 通知传感器更新
            self.async_set_updated_data(self._data_cache)

    async def _async_update_data(self):
        """Update data via API."""
        try:
            # 使用正确的日期时间格式
            current_time = dt_util.now().strftime("%Y-%m-%d %H:%M")
            
            # 并行获取所有数据
            tasks = [
                self._fetch_hot_news(),
                self._fetch_oil_price(),
                self._fetch_exchange_rate(),
                self._fetch_air_quality()
            ]
            
            today_hot, today_oil, today_rate, today_air = await asyncio.gather(*tasks)
            
            # 记录成功更新时间
            self._last_successful_update = current_time
            
            data = {
                "today_hot": today_hot,
                "today_oil": today_oil,
                "today_rate": today_rate,
                "today_air": today_air,
                "last_update": current_time
            }
            
            # 更新缓存
            self._data_cache = data
            return data
            
        except Exception as err:
            _LOGGER.error("Error updating Tian Realtime data: %s", err)
            current_time = dt_util.now().strftime("%Y-%m-%d %H:%M")
            return {
                "today_hot": {"detail": "更新失败", "error": str(err)},
                "today_oil": {"detail": "更新失败", "error": str(err)},
                "today_rate": {"detail": "更新失败", "error": str(err)},
                "today_air": {"detail": "更新失败", "error": str(err)},
                "last_update": current_time
            }

    async def _fetch_hot_news(self):
        """Fetch hot news from API."""
        try:
            url = f"{API_BASE_URL}{API_HOT_NEWS}"
            params = {"key": self.api_key}
        
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == 200:
                        result = data.get("result", {})
                        news_list = result.get("list", [])
                    
                        # 构建hot_data对象
                        hot_data = {}
                        for idx, item in enumerate(news_list, 1):
                            hot_data[str(idx)] = item.get("word", f"新闻{idx}")
                    
                        self._hot_data = hot_data
                    
                        # 随机选择一个新闻作为初始显示
                        if hot_data:
                            random_key = random.choice(list(hot_data.keys()))
                            current_news = hot_data[random_key]
                            self._current_hot_index = int(random_key) - 1
                        
                            return {
                                "detail": f"📰头条：{current_news}",
                                "hot_data": hot_data,
                                "hot_index": self._current_hot_index + 1
                            }
            
                return {
                    "detail": "暂无新闻", 
                    "hot_data": {},
                    "hot_index": 0
                }
            
        except Exception as err:
            _LOGGER.error("Error fetching hot news: %s", err)
            return {
                "detail": f"获取失败: {err}", 
                "error": str(err),
                "hot_data": {},
                "hot_index": 0
            }

    async def _fetch_oil_price(self):
        """Fetch oil price from API."""
        try:
            url = f"{API_BASE_URL}{API_OIL_PRICE}"
            params = {"key": self.api_key, "prov": self.oil_province}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == 200:
                        result = data.get("result", {})
                        return {
                            "detail": f"⛽油价：0#{result.get('p0', 'N/A')}元 92#{result.get('p92', 'N/A')}元 95#{result.get('p95', 'N/A')}元",
                            "full_data": result
                        }
                return {
                    "detail": "暂无油价信息", 
                    "full_data": {}
                }
        except Exception as err:
            _LOGGER.error("Error fetching oil price: %s", err)
            return {
                "detail": f"获取失败: {err}", 
                "error": str(err)
            }

    async def _fetch_exchange_rate(self):
        """Fetch exchange rate from API."""
        try:
            url = f"{API_BASE_URL}{API_EXCHANGE_RATE}"
            # 使用正确的参数
            params = {
                "key": self.api_key,
                "fromcoin": "USD",
                "tocoin": "CNY",
                "money": "100"
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == 200:
                        result = data.get("result", {})
                        # 根据新API的响应格式调整
                        exchange_rate = result.get("money", 0)
                        # 格式化汇率为两位小数
                        formatted_rate = f"{float(exchange_rate):.2f}" if exchange_rate else "0.00"
                        return {
                            "detail": f"💵汇率：$100美元兑人民币¥{formatted_rate}元",
                            "full_data": result
                        }
                return {
                    "detail": "暂无汇率信息", 
                    "full_data": {}
                }
        except Exception as err:
            _LOGGER.error("Error fetching exchange rate: %s", err)
            return {
                "detail": f"获取失败: {err}", 
                "error": str(err)
            }

    async def _fetch_air_quality(self):
        """Fetch air quality from API."""
        try:
            url = f"{API_BASE_URL}{API_AIR_QUALITY}"
            params = {"key": self.api_key, "area": self.air_city}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == 200:
                        result = data.get("result", {})
                        return {
                            "detail": f"⛅空气：{result.get('quality', 'N/A')} AQI:{result.get('aqi', 'N/A')} PM2.5:{result.get('pm2_5', 'N/A')} SO2:{result.get('so2', 'N/A')}",
                            "full_data": result
                        }
                return {
                    "detail": "暂无空气质量信息", 
                    "full_data": {}
                }
        except Exception as err:
            _LOGGER.error("Error fetching air quality: %s", err)
            return {
                "detail": f"获取失败: {err}", 
                "error": str(err)
            }

    def get_scroll_data(self):
        """Get data for scrolling display."""
        if not self._data_cache:
            return {}
        
        # 获取当前头条内容
        current_hot_detail = ""
        if self._hot_data and len(self._hot_data) > 0:
            current_index = (self._current_hot_index % len(self._hot_data)) + 1
            current_hot_detail = self._hot_data.get(str(current_index), "")
        
        return {
            "title": "📚实时动态",
            "title1": "实时动态",  # 添加title1属性
            "title2": "今日动态",  # 添加title2属性
            "hot_detail": f"📰头条：{current_hot_detail}" if current_hot_detail else "📰头条：暂无新闻",
            "oil_detail": self._data_cache.get("today_oil", {}).get("detail", ""),
            "rate_detail": self._data_cache.get("today_rate", {}).get("detail", ""),
            "air_detail": self._data_cache.get("today_air", {}).get("detail", ""),
            "hot_index": self._current_hot_index + 1,
            "update_time": self._last_successful_update  # 添加更新时间属性
        }