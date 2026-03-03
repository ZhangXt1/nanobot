---
name: browser
description: 浏览器控制 - 基于playwright实现浏览器自动化操作 (优化版)
---

# 浏览器控制

基于playwright实现浏览器自动化操作，支持网页抓取、表单填写、截图等功能。

## 优化历史

**2026-03-03 优化:**
1. 默认使用非无头模式(headless=false)，避免被网站检测
2. 改用domcontentloaded + 手动等待，避免网络请求导致的超时
3. 添加反检测参数(--disable-blink-features=AutomationControlled)
4. 自动先访问主页加载Cookies
5. 增加wait_time参数可调
6. 添加JavaScript直接提取功能(js_evaluate)

## 功能

### 1. 网页抓取
- 动态页面内容抓取（JavaScript渲染）
- 静态页面内容提取
- 指定元素提取
- JavaScript直接提取

### 2. 浏览器操作
- 打开网页
- 点击元素
- 填写表单
- 滚动页面
- 截图

### 3. 反检测特性
- 隐藏自动化特征
- 使用真实浏览器(User-Agent)
- 智能等待渲染

## 使用方法

### 获取页面内容 (推荐)
```
browser(action="content", url="https://gushitong.baidu.com/stock/sh000001")
```

### SPA应用 (等待更长时间)
```
browser(action="content", url="https://example.com", wait_time=10)
```

### JavaScript直接提取数据
```
browser(action="evaluate", url="https://example.com", js_evaluate="return document.body.innerText")
```

### 截图
```
browser(action="screenshot", url="https://example.com")
```

### 点击元素
```
browser(action="click", url="https://example.com", selector="#submit-button")
```

### 填写表单
```
browser(action="fill", url="https://example.com", selector="#username", value="myuser")
```

### 执行JavaScript
```
browser(action="script", url="https://example.com", script="return document.title")
```

### 批量提取元素
```
browser(action="evaluate", url="https://example.com", selectors=["h1", ".price", "#submit"])
```

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| action | str | "help" | 操作类型 |
| url | str | - | 页面URL |
| selector | str | None | CSS选择器 |
| selectors | list | [] | 选择器列表 |
| headless | bool | False | 是否无头模式 |
| wait_time | int | 6 | 等待渲染秒数 |
| max_chars | int | 5000 | 最大字符数 |
| full_page | bool | False | 是否截取全页 |
| value | str | - | 表单填写值 |
| script | str | - | JavaScript脚本 |
| js_evaluate | str | None | JavaScript提取脚本 |
| check_errors | list | ["服务异常","加载失败"] | 错误检查 |

## 常见问题

### 1. 页面显示"服务异常"
- 原因：被网站检测为机器人
- 解决：设置 `headless=false` 或增加 `wait_time=10`

### 2. 超时
- 原因：`wait_until="networkidle"` 等待持续的网络请求
- 解决：改用 `wait_until="domcontentloaded"` + `wait_time`

### 3. 需要登录/Cookies
- 解决：系统会自动先访问域名主页加载Cookies

### 4. 数据未加载
- 解决：增加 `wait_time` 到 8-10 秒

## 依赖

- Python playwright包
- Chromium/Edge浏览器

## 安装

```bash
pip install playwright
playwright install chromium
# Windows推荐使用Edge:
# 系统会自动使用channel='msedge'
```
