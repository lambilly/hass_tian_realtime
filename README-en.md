# Tianju Data - Real-time Updates Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

This is a custom integration for Home Assistant that fetches real-time data through Tianju Data API, including headline news, oil prices, exchange rates, and air quality information.

## Features

- 💵 **USD Exchange Rate**: USD to RMB exchange rate (updated daily at 7:00/17:00)
- ⛽ **Today's Oil Prices**: Latest oil prices across provinces and cities in China (updated daily at 7:00/17:00)
- 🌤️ **Air Quality**: Air quality index for prefecture-level cities nationwide (updated daily at 7:00/17:00)
- 📰 **Headline News**: 50 current hot topics from today's headlines (updated daily at 7:00/17:00)
- 📰 **Scrolling Content**: Automatically scrolls through today's hot topics (configurable scroll interval)
- ⚙️ **Highly Configurable**: Customizable update intervals and scroll intervals
- 🌏 **Multi-region Support**: Supports oil price queries for 31 provinces/cities and air quality queries for 300+ prefecture-level cities

## Installation Methods

### Method 1: Via HACS Installation (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed
2. Click "Integrations" in HACS
3. Click the three dots in the upper right corner, select "Custom repositories"
4. Add repository URL: `https://github.com/lambilly/hass_tian_realtime`
5. Select category as "Integration"
6. Search for "Tianju Data - Real-time Updates" and install
7. Restart Home Assistant

### Method 2: Manual Installation

1. Download the integration files
2. Copy the `custom_components/tian_realtime` folder to the `custom_components` folder in your Home Assistant configuration directory
3. Restart Home Assistant

## Configuration

### Configuration via UI

1. Go to Home Assistant "Configuration" -> "Devices & Services"
2. Click "Add Integration"
3. Search for "Tianju Data - Real-time Updates"
4. Follow the prompts to fill in the following information:
   - **API Key**: Apply from Tianju Data official website
   - **Oil Price Province**: Select your province
   - **Air Quality City**: Enter your city
   - **Data Update Interval**: Updated daily at 7:00/17:00
   - **Headline Scroll Interval**: 5-300 seconds (default 15 seconds)

### Tianju Data API Application

1. Visit [Tianju Data Official Website](https://www.tianapi.com/)
2. Register an account and log in
3. Apply for API key in the console
4. Ensure the following interfaces are activated:
   - Headline Hot Search List
   - Real-time Oil Prices
   - Exchange Rate Query
   - Air Quality Index

## Generated Entities

The integration will create the following sensor entities:

| Entity Name | Entity ID | Description | Icon |
|-------------|-----------|-------------|------|
| Headline News | `sensor.toutiao_xin_wen` | Hot news information | `mdi:newspaper-variant-multiple` |
| Today's Oil Prices | `sensor.jin_ri_you_jia` | Oil prices for specified province | `mdi:gas-station` |
| USD Exchange Rate | `sensor.mei_yuan_hui_lv` | USD to RMB exchange rate | `mdi:currency-usd` |
| Air Quality | `sensor.kong_qi_zhi_liang` | Air quality for specified city | `mdi:air-filter` |
| Scrolling Content | `sensor.gun_dong_nei_rong` | Rotating display of all information | `mdi:chart-box-outline` |

## Device Information

All entities belong to a device named "Real-time Updates" for unified management.

## Attribute Description

### Scrolling Content Entity Attributes

- `title` - Real-time updates title with icon
- `title1` - Real-time updates title without icon
- `title2` - Today's updates title
- `hot_detail` - Currently displayed headline news
- `oil_detail` - Oil price information
- `rate_detail` - Exchange rate information
- `air_detail` - Air quality information
- `hot_index` - Current headline news index number
- `update_time` - Current headline news update time

### Headline News Entity Attributes

- `detail` - Currently displayed headline content
- `hot_data` - Dictionary of all headline news (items 1-50)
- `hot_index` - Currently displayed news index number

## Automation Examples

### Send Notification When Air Quality Deteriorates

```yaml
automation:
  - alias: "Air Quality Alert"
    trigger:
      platform: state
      entity_id: sensor.kong_qi_zhi_liang
    condition:
      condition: template
      value_template: >
        {{ state_attr('sensor.kong_qi_zhi_liang', 'detail') | regex_search('AQI:(\\d+)', '\\1') | int > 100 }}
    action:
      service: notify.mobile_app
      data:
        message: "Air quality deteriorated: {{ states('sensor.kong_qi_zhi_liang') }}"
```

### Display Scrolling Information on Dashboard (Requires HACS installation: Lovelace HTML Jinja2 Template card)

```yaml
type: custom:html-template-card
content: >-
  <div
  style="color: white;"><p align=left><h3 style="color: white; margin-bottom:
  0px;">【📋Real-time Updates】</h3> </p> </div>    <p align= left style="color:
  white; font-size: 1.0em; margin-top: 10px;">{{ state_attr('sensor.gun_dong_nei_rong','hot_detail') }}
  <br>{{ state_attr('sensor.gun_dong_nei_rong','rate_detail') }}
  <br>{{ state_attr('sensor.gun_dong_nei_rong','oil_detail') }}
  <br>{{ state_attr('sensor.gun_dong_nei_rong','air_detail') }}
  </p>
```

## Troubleshooting

### Common Issues

1. **API Call Failures**
   - Check if API key is correct
   - Confirm relevant interfaces are activated
   - Check Home Assistant logs for detailed error information

2. **Data Not Updating**
   - Check network connection
   - Confirm update interval settings are reasonable
   - Restart the integration

3. **Entities Unavailable**
   - Restart Home Assistant
   - Check integration configuration

### Debug Logging

Add the following configuration to configuration.yaml to enable detailed logging:

```yaml
logger:
  default: info
  logs:
    custom_components.tian_realtime: debug
```

## Support & Feedback

If you encounter problems or have suggestions, please contact us through:

- Submit an Issue in the GitHub repository
- Send email to: your email address

## License

This project uses the MIT License
- See LICENSE file for details.
