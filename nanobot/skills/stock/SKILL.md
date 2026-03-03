---
name: stock
description: 股票咨询查询 - 使用akshare实现股票、指数、基金、新闻等数据的查询
---

# 股票咨询查询

使用akshare库获取A股、港股、美股行情，提供股票、指数、基金、财经新闻查询。

## 功能

### 1. 股票行情查询
- A股实时行情（代码、名称、现价、涨跌幅、成交量等）
- 港股实时行情
- 美股实时行情
- 历史K线数据

### 2. 指数查询
- A股主要指数（上证指数、深证成指、创业板指等）
- 港股指数（恒生指数等）
- 美股指数（道琼斯、纳斯达克、标普500等）

### 3. 基金查询
- 基金净值查询
- 基金详细信息

### 4. 财经新闻
- 财经要闻
- 个股新闻

## 使用方法

### 查询股票行情
```
stock(action="quote", symbol="600519")  # 茅台
stock(action="quote", symbol="000001")  # 平安银行
stock(action="quote", symbol="00700")   # 腾讯控股(港股)
stock(action="quote", symbol="AAPL")    # 苹果(美股)
```

### 查询指数
```
stock(action="index", symbol="000001")  # 上证指数
stock(action="index", symbol="399001")  # 深证成指
stock(action="index", symbol="HSI")     # 恒生指数
stock(action="index", symbol="DJI")     # 道琼斯
```

### 查询基金净值
```
stock(action="fund", code="110022")  # 基金代码
```

### 查询财经新闻
```
stock(action="news", count=10)
```

### 查看帮助
```
stock(action="help")
```

## 注意事项

- A股代码：6位数字（上证以6开头，深证以0/3开头）
- 港股代码：5位数字
- 美股代码：字母缩写（如AAPL、MSFT）
- 需要网络连接获取数据
