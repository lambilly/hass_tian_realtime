"""Constants for Tian Realtime integration."""

DOMAIN = "tian_realtime"
NAME = "天聚数行-实时动态"

CONF_API_KEY = "api_key"
CONF_OIL_PROVINCE = "oil_province"
CONF_AIR_CITY = "air_city"
CONF_SCROLL_INTERVAL = "scroll_interval"

# 确保没有 CONF_UPDATE_INTERVAL 相关常量
DEFAULT_SCROLL_INTERVAL = 15
MIN_SCROLL_INTERVAL = 5
MAX_SCROLL_INTERVAL = 300

# API endpoints
API_BASE_URL = "https://apis.tianapi.com"
API_HOT_NEWS = "/toutiaohot/index"
API_OIL_PRICE = "/oilprice/index"
API_EXCHANGE_RATE = "/fxrate/index"
API_AIR_QUALITY = "/aqi/index"

# Entity names
ENTITY_HOT_NEWS = "头条新闻"
ENTITY_OIL_PRICE = "今日油价"
ENTITY_EXCHANGE_RATE = "美元汇率"
ENTITY_AIR_QUALITY = "空气质量"
ENTITY_SCROLL_CONTENT = "滚动内容"