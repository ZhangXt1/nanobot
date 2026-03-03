"""
浏览器控制 - browser skill (优化版)
基于playwright实现浏览器自动化操作

优化内容 (2026-03-03):
1. 支持非无头模式，避免被网站检测
2. 优化页面加载策略，避免超时
3. 添加反检测参数
4. 支持先访问主页加载Cookies
5. 增加等待时间选项
6. 更友好的错误处理
"""

import asyncio
import base64
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# 尝试导入playwright
try:
    from playwright.async_api import async_playwright, Error as PlaywrightError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


# 截图保存目录
SCREENSHOT_DIR = Path("D:/Code/nanobot-xiao/.workspace/photos")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


async def _get_browser_context(
    headless: bool = False,
    use_edge: bool = True,
    bypass_detection: bool = True,
    wait_time: int = 5
):
    """
    获取浏览器上下文
    
    Args:
        headless: 是否使用无头模式 (某些网站会检测，建议默认False)
        use_edge: 是否使用Edge浏览器 (Windows推荐)
        bypass_detection: 是否隐藏自动化特征
        wait_time: 页面加载后等待秒数
    
    Returns:
        (playwright, browser, context, page, wait_time)
    """
    if not PLAYWRIGHT_AVAILABLE:
        raise ImportError("playwright未安装，请运行: pip install playwright && playwright install chromium")
    
    try:
        playwright = await async_playwright().start()
        
        # 启动参数
        launch_options = {}
        
        if use_edge:
            launch_options['channel'] = 'msedge'
        
        if bypass_detection:
            # 隐藏自动化特征，避免被检测
            launch_options['args'] = [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        
        launch_options['headless'] = headless
        
        browser = await playwright.chromium.launch(**launch_options)
        
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        # 添加反检测脚本
        if bypass_detection:
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
        
        return playwright, browser, context, page, wait_time
        
    except Exception as e:
        raise RuntimeError(f"启动浏览器失败: {str(e)}")


async def _close_browser(playwright, browser, context, page):
    """关闭浏览器"""
    try:
        await page.close()
        await context.close()
        await browser.close()
        await playwright.stop()
    except:
        pass


async def _run_browser_action(action_func, **kwargs):
    """运行浏览器操作"""
    try:
        headless = kwargs.get('headless', False)
        use_edge = kwargs.get('use_edge', True)
        bypass_detection = kwargs.get('bypass_detection', True)
        wait_time = kwargs.get('wait_time', 5)
        
        result = await _get_browser_context(
            headless=headless,
            use_edge=use_edge,
            bypass_detection=bypass_detection,
            wait_time=wait_time
        )
        playwright, browser, context, page, actual_wait = result
        
        try:
            # 传递wait_time给action_func
            result = await action_func(page, actual_wait)
        finally:
            await _close_browser(playwright, browser, context, page)
        return result
    except ImportError as e:
        return f"[error] {str(e)}"
    except Exception as e:
        return f"[error] 浏览器操作失败: {str(e)}"


async def action_goto(url: str, headless: bool = False, wait_time: int = 5) -> str:
    """打开网页"""
    async def _action(page, wait_time):
        # 使用domcontentloaded避免网络请求导致的超时
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        # 等待JavaScript渲染
        time.sleep(wait_time)
        
        title = await page.title()
        content = await page.content()
        return f"[OK] 已打开: {url}\n\n标题: {title}\n\n内容长度: {len(content)} 字符"
    
    return await _run_browser_action(_action, headless=headless, wait_time=wait_time)


async def action_content(
    url: str, 
    selector: str = None, 
    max_chars: int = 5000,
    headless: bool = False,
    wait_time: int = 6,
    check_errors: List[str] = None
) -> str:
    """
    获取页面内容
    
    Args:
        url: 页面URL
        selector: 可选，指定元素选择器
        max_chars: 最大字符数
        headless: 是否无头模式
        wait_time: 等待渲染时间(秒)
        check_errors: 检查页面是否包含错误信息，如["服务异常", "加载失败"]
    """
    if check_errors is None:
        check_errors = ["服务异常", "加载失败", "重新加载"]
    
    async def _action(page, wait_time):
        # 先访问主页加载Cookies（重要！）
        base_url = "/".join(url.split("/")[:3])  # 提取域名
        try:
            await page.goto(base_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
        except:
            pass
        
        # 访问目标页面
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(wait_time)
        
        # 检查是否有错误
        body_text = await page.evaluate("document.body.innerText")
        for err in check_errors:
            if err in body_text:
                return f"[warn] 页面显示: {err}，数据可能未加载完成\n\n如需等待更长时间，可设置 wait_time=10"
        
        if selector:
            elements = await page.query_selector_all(selector)
            content_parts = []
            for el in elements[:10]:
                text = await el.inner_text()
                if text:
                    content_parts.append(text.strip())
            content = "\n\n".join(content_parts)
        else:
            body = await page.query_selector("body")
            content = await body.inner_text() if body else ""
        
        if len(content) > max_chars:
            content = content[:max_chars] + "..."
        
        return f"[OK] 页面内容 ({url}):\n\n{content}"
    
    return await _run_browser_action(_action, headless=headless, wait_time=wait_time)


async def action_screenshot(
    url: str, 
    selector: str = None, 
    full_page: bool = False,
    headless: bool = False,
    wait_time: int = 5
) -> str:
    """页面截图"""
    async def _action(page, wait_time):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"browser_{timestamp}.png"
        filepath = SCREENSHOT_DIR / filename
        
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(wait_time)
        
        if selector:
            element = await page.query_selector(selector)
            if element:
                await element.screenshot(path=str(filepath))
            else:
                return f"[error] 未找到元素: {selector}"
        else:
            await page.screenshot(path=str(filepath), full_page=full_page)
        
        with open(filepath, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode()
        
        return f"[OK] 截图已保存: {filename}\n\n📷 [图片]({filepath})"
    
    return await _run_browser_action(_action, headless=headless, wait_time=wait_time)


async def action_click(
    url: str, 
    selector: str,
    headless: bool = False,
    wait_time: int = 3
) -> str:
    """点击元素"""
    async def _action(page, wait_time):
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(wait_time)
        
        await page.wait_for_selector(selector, timeout=10000)
        await page.click(selector)
        
        await asyncio.sleep(1)
        
        return f"[OK] 已点击元素: {selector}\n\n页面标题: {await page.title()}"
    
    return await _run_browser_action(_action, headless=headless, wait_time=wait_time)


async def action_fill(
    url: str, 
    selector: str, 
    value: str,
    headless: bool = False,
    wait_time: int = 3
) -> str:
    """填写表单"""
    async def _action(page, wait_time):
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(wait_time)
        
        await page.wait_for_selector(selector, timeout=10000)
        await page.fill(selector, value)
        
        filled_value = await page.input_value(selector)
        
        return f"[OK] 已填写表单\n\n选择器: {selector}\n填写内容: {filled_value}"
    
    return await _run_browser_action(_action, headless=headless, wait_time=wait_time)


async def action_script(
    url: str, 
    script: str,
    headless: bool = False,
    wait_time: int = 5
) -> str:
    """执行JavaScript"""
    async def _action(page, wait_time):
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(wait_time)
        
        result = await page.evaluate(script)
        
        return f"[OK] JavaScript执行结果:\n\n{result}"
    
    return await _run_browser_action(_action, headless=headless, wait_time=wait_time)


async def action_evaluate(
    url: str, 
    selectors: List[str],
    headless: bool = False,
    wait_time: int = 6,
    js_evaluate: str = None
) -> str:
    """
    批量获取多个元素的内容
    
    Args:
        url: 页面URL
        selectors: CSS选择器列表
        headless: 是否无头模式
        wait_time: 等待渲染时间
        js_evaluate: 可选的JavaScript提取脚本
    """
    async def _action(page, wait_time):
        # 先访问主页加载Cookies
        base_url = "/".join(url.split("/")[:3])
        try:
            await page.goto(base_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
        except:
            pass
        
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(wait_time)
        
        results = {}
        
        # 如果提供了JavaScript提取脚本
        if js_evaluate:
            try:
                js_result = await page.evaluate(js_evaluate)
                return f"[OK] JavaScript提取结果:\n\n{js_result}"
            except Exception as e:
                return f"[error] JavaScript执行失败: {str(e)}"
        
        # 否则使用选择器提取
        for sel in selectors:
            try:
                elements = await page.query_selector_all(sel)
                texts = []
                for el in elements[:5]:
                    text = await el.inner_text()
                    if text:
                        texts.append(text.strip())
                results[sel] = texts
            except Exception as e:
                results[sel] = [f"Error: {str(e)}"]
        
        msg = "[OK] 元素提取结果:\n\n"
        for sel, texts in results.items():
            msg += f"**{sel}**:\n"
            for i, text in enumerate(texts, 1):
                if len(text) > 100:
                    text = text[:100] + "..."
                msg += f"  {i}. {text}\n"
            msg += "\n"
        
        return msg
    
    return await _run_browser_action(_action, headless=headless, wait_time=wait_time)


def action_help() -> str:
    """帮助信息"""
    return """# 浏览器控制使用指南 (优化版)

## 安装依赖:
```bash
pip install playwright
playwright install chromium
```

## 重要更新 (2026-03-03):
1. 默认使用非无头模式，避免被网站检测
2. 使用domcontentloaded+手动等待，避免超时
3. 自动先访问主页加载Cookies
4. 添加反检测参数

## 打开网页:
browser(action="goto", url="https://www.example.com")
browser(action="goto", url="https://example.com", headless=true)

## 获取页面内容 (推荐用于SPA应用):
browser(action="content", url="https://gushitong.baidu.com/stock/sh000001")
browser(action="content", url="https://example.com", selector=".article", wait_time=8)

## 截图:
browser(action="screenshot", url="https://example.com")
browser(action="screenshot", url="https://example.com", full_page=true)

## 点击元素:
browser(action="click", url="https://example.com", selector="#submit-btn")

## 填写表单:
browser(action="fill", url="https://example.com", selector="#username", value="myuser")

## 执行JavaScript:
browser(action="script", url="https://example.com", script="return document.title")

## 批量提取元素 (支持JavaScript提取):
browser(action="evaluate", url="https://example.com", selectors=["h1", ".price"])
browser(action="evaluate", url="https://example.com", js_evaluate="return document.body.innerText")


## 参数说明:
- headless: 是否无头模式 (默认false，建议保持)
- wait_time: 页面加载后等待秒数 (默认5-6，SPA应用建议8+)
- selector: CSS选择器
- selectors: 选择器列表
- js_evaluate: JavaScript提取脚本
- check_errors: 检查页面错误信息列表

## 常见问题:
1. 页面显示"服务异常": 使用 headless=false 或增加 wait_time
2. 超时: 改用 domcontentloaded + wait_time
3. 需要Cookies: 系统会自动先访问主页加载Cookies
"""


def run(action: str = "help", **kwargs) -> str:
    """
    主运行函数
    
    Args:
        action: 操作类型 (goto/content/screenshot/click/fill/script/evaluate/help)
        **kwargs: 其他参数
            - url: 页面URL
            - selector: CSS选择器
            - selectors: 选择器列表
            - headless: 是否无头模式 (默认False)
            - wait_time: 等待时间 (默认5-6秒)
            - max_chars: 最大字符数
            - full_page: 是否截取全页
            - value: 填写表单的值
            - script: JavaScript脚本
            - js_evaluate: JavaScript提取脚本
            - check_errors: 错误检查列表
    
    Returns:
        操作结果
    """
    if not PLAYWRIGHT_AVAILABLE:
        return "[error] playwright未安装\n\n请运行以下命令安装:\npip install playwright\nplaywright install chromium"
    
    # 默认参数
    headless = kwargs.get('headless', False)  # 默认非无头
    wait_time = kwargs.get('wait_time', 6)     # 默认6秒等待
    
    action_map = {
        "goto": lambda: asyncio.run(action_goto(
            url=kwargs.get("url", ""),
            headless=headless,
            wait_time=wait_time
        )),
        "content": lambda: asyncio.run(action_content(
            url=kwargs.get("url", ""),
            selector=kwargs.get("selector"),
            max_chars=kwargs.get("max_chars", 5000),
            headless=headless,
            wait_time=kwargs.get("wait_time", wait_time),
            check_errors=kwargs.get("check_errors")
        )),
        "screenshot": lambda: asyncio.run(action_screenshot(
            url=kwargs.get("url", ""),
            selector=kwargs.get("selector"),
            full_page=kwargs.get("full_page", False),
            headless=headless,
            wait_time=kwargs.get("wait_time", wait_time)
        )),
        "click": lambda: asyncio.run(action_click(
            url=kwargs.get("url", ""),
            selector=kwargs.get("selector", ""),
            headless=headless,
            wait_time=kwargs.get("wait_time", 3)
        )),
        "fill": lambda: asyncio.run(action_fill(
            url=kwargs.get("url", ""),
            selector=kwargs.get("selector", ""),
            value=kwargs.get("value", ""),
            headless=headless,
            wait_time=kwargs.get("wait_time", 3)
        )),
        "script": lambda: asyncio.run(action_script(
            url=kwargs.get("url", ""),
            script=kwargs.get("script", ""),
            headless=headless,
            wait_time=kwargs.get("wait_time", wait_time)
        )),
        "evaluate": lambda: asyncio.run(action_evaluate(
            url=kwargs.get("url", ""),
            selectors=kwargs.get("selectors", []),
            headless=headless,
            wait_time=kwargs.get("wait_time", wait_time),
            js_evaluate=kwargs.get("js_evaluate")
        )),
        "help": action_help
    }
    
    if action not in action_map:
        return f"[error] 未知操作: {action}\n\n{action_help()}"
    
    return action_map[action]()


if __name__ == "__main__":
    print(run("help"))
