# 天聚数行-实时动态 Home Assistant 集成

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

这是一个用于 Home Assistant 的自定义集成，通过天聚数行 API 获取实时数据，包括头条新闻、油价、汇率和空气质量信息。

## 功能特性

- 💵 **美元汇率**：美元兑人民币汇率（24小时更新一次）
- ⛽ **今日油价**：全国各省市最新油价（24小时更新一次）
- 🌤️ **空气质量**：全国地级市空气质量指数（24小时更新一次）
- 📰 **头条新闻**：自动滚动显示今日头条热点（可配置滚动间隔）
- ⚙️ **高度可配置**：可设置更新间隔和滚动间隔
- 🌏 **多地区支持**：支持全国31个省市油价查询和300+地级市空气质量查询

## 安装方式

### 方法一：通过 HACS 安装（推荐）

1. 确保已安装 [HACS](https://hacs.xyz/)
2. 在 HACS 中点击「集成」
3. 点击右上角三个点，选择「自定义仓库」
4. 添加仓库地址：`https://github.com/lambilly/hass_tian_realtime`
5. 选择分类为「集成」
6. 搜索「天聚数行-实时动态」并安装
7. 重启 Home Assistant

### 方法二：手动安装

1. 下载本集成文件
2. 将 `custom_components/tian_realtime` 文件夹复制到您的 Home Assistant 配置目录中的 `custom_components` 文件夹
3. 重启 Home Assistant

## 配置

### 通过界面配置

1. 进入 Home Assistant「配置」->「设备与服务」
2. 点击「添加集成」
3. 搜索「天聚数行-实时动态」
4. 按照提示填写以下信息：
   - **API 密钥**：从天聚数行官网申请
   - **油价省份**：选择您所在的省份
   - **空气质量城市**：输入您所在的城市
   - **数据更新间隔**：60-43200分钟（默认1440分钟）
   - **头条滚动间隔**：5-300秒（默认15秒）

### 天行数据 API 申请

1. 访问 [天行数据官网](https://www.tianapi.com/)
2. 注册账号并登录
3. 在控制台申请 API 密钥
4. 确保已开通以下接口：
   - 头条热搜榜
   - 实时油价
   - 汇率查询
   - 空气质量指数

## 生成的实体

集成将创建以下传感器实体：

| 实体名称 | 实体ID | 描述 | 图标 |
|---------|--------|------|------|
| 头条新闻 | `sensor.toutiao_xin_wen` | 热点新闻信息 | `mdi:newspaper-variant-multiple` |
| 今日油价 | `sensor.jin_ri_you_jia` | 指定省份油价 | `mdi:gas-station` |
| 美元汇率 | `sensor.mei_yuan_hui_lv` | 美元兑人民币汇率 | `mdi:currency-usd` |
| 空气质量 | `sensor.kong_qi_zhi_liang` | 指定城市空气质量 | `mdi:air-filter` |
| 滚动内容 | `sensor.gun_dong_nei_rong` | 所有信息的滚动展示 | `mdi:chart-box-outline` |

## 设备信息

所有实体都归属于名为「实时动态」的设备，方便统一管理。

## 属性说明

### 滚动内容实体属性

- `hot_detail` - 当前显示的头条新闻
- `oil_detail` - 油价信息
- `rate_detail` - 汇率信息  
- `air_detail` - 空气质量信息
- `hot_index` - 当前头条新闻的序号

### 头条新闻实体属性

- `detail` - 当前显示的头条内容
- `hot_data` - 所有头条新闻的字典（1-50条）
- `hot_index` - 当前显示的新闻序号

## 自动化示例

### 当空气质量变差时发送通知

```yaml
automation:
  - alias: "空气质量警告"
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
        message: "空气质量变差：{{ states('sensor.kong_qi_zhi_liang') }}"
```
### 在仪表板上显示滚动信息
```yaml
type: entities
entities:
  - entity: sensor.gun_dong_nei_rong
    name: 实时信息
    secondary_info: last-changed
```
## 故障排除
### 常见问题
1.	API 调用失败
o	检查 API 密钥是否正确
o	确认已开通相应接口
o	查看 Home Assistant 日志获取详细错误信息
2.	数据不更新
o	检查网络连接
o	确认更新间隔设置合理
o	重启集成
3.	实体不可用
o	重启 Home Assistant
o	检查集成配置
### 日志调试
在 configuration.yaml 中添加以下配置开启详细日志：
```yaml
logger:
  default: info
  logs:
    custom_components.tian_realtime: debug
```
## 支持与反馈
如果您遇到问题或有建议，请通过以下方式联系：
•	在 GitHub 仓库提交 Issue
•	发送邮件至：你的邮箱
## 许可证
本项目采用 MIT 许可证 - 查看 LICENSE 文件了解详情。
## 更新日志
v1.0.0
•	初始版本发布
•	支持头条新闻、油价、汇率、空气质量数据
•	实现滚动显示功能

