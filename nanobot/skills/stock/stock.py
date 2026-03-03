"""
股票咨询查询 - stock skill
使用akshare实现股票、指数、基金、新闻等数据的查询
"""

import akshare as ak
import pandas as pd
from typing import Optional, Dict, Any, List


def _format_money(num: float) -> str:
    """格式化金额（亿/万）"""
    if abs(num) >= 1e8:
        return f"{num/1e8:.2f}亿"
    elif abs(num) >= 1e4:
        return f"{num/1e4:.2f}万"
    return f"{num:.2f}"


def _get_stock_type(symbol: str) -> str:
    """判断股票市场类型"""
    symbol = str(symbol).strip().upper()
    
    # 纯数字（A股或港股）
    if symbol.isdigit():
        if len(symbol) == 6:
            if symbol.startswith('6'):
                return 'sh'  # 上证
            elif symbol.startswith(('0', '3')):
                return 'sz'  # 深证
        elif len(symbol) == 5:
            return 'hk'  # 港股
    
    # 美股代码映射
    us_stocks = {
        'AAPL': '苹果', 'MSFT': '微软', 'GOOGL': '谷歌', 'AMZN': '亚马逊',
        'META': 'Meta', 'TSLA': '特斯拉', 'NVDA': '英伟达', 'JPM': '摩根大通',
        'V': 'Visa', 'JNJ': '强生', 'WMT': '沃尔玛', 'PG': '宝洁',
        'MA': '万事达', 'UNH': '联合健康', 'HD': '家得宝', 'DIS': '迪士尼',
        'BAC': '美国银行', 'NFLX': 'Netflix', 'ADBE': 'Adobe', 'CRM': 'Salesforce',
        'INTC': '英特尔', 'AMD': 'AMD', 'PYPL': 'PayPal', 'CSCO': '思科',
        'KO': '可口可乐', 'PEP': '百事', 'NKE': '耐克', 'MRK': '默克',
        'ABT': '雅培', 'T': 'AT&T', 'VZ': '威瑞森', 'XOM': '埃克森美孚',
        'CVX': '雪佛龙'
    }
    if symbol in us_stocks:
        return 'us'
    
    return 'unknown'


def action_quote(symbol: str) -> str:
    """
    查询股票行情
    
    Args:
        symbol: 股票代码（支持A股、港股、美股）
    
    Returns:
        股票行情信息
    """
    try:
        stock_type = _get_stock_type(symbol)
        
        if stock_type == 'unknown':
            return f"❌ 无法识别股票代码: {symbol}"
        
        # A股
        if stock_type in ['sh', 'sz']:
            # 使用 stock_bid_ask_em 接口查询单只股票的行情报价
            if stock_type == 'sh':
                code = f"{symbol}.SH"
            else:
                code = f"{symbol}.SZ"
            
            try:
                df = ak.stock_bid_ask_em(symbol=code)
                if df.empty:
                    return f"❌ 未找到股票: {symbol}"
                
                # 提取股票基本信息
                name = df.iloc[0]['名称']
                price = df.iloc[0]['最新价']
                change = df.iloc[0]['涨跌幅']
                volume = df.iloc[0]['成交量']
                amount = df.iloc[0]['成交额']
                amplitude = df.iloc[0]['振幅']
                high = df.iloc[0]['最高']
                low = df.iloc[0]['最低']
                open_price = df.iloc[0]['今开']
                pre_close = df.iloc[0]['昨收']
            except Exception as e:
                # 尝试使用其他接口作为备用
                try:
                    df = ak.stock_zh_a_spot_em()
                    row = df[df['代码'] == code]
                    if row.empty:
                        return f"❌ 未找到股票: {symbol}"
                    
                    row = row.iloc[0]
                    name = row['名称']
                    price = row['最新价']
                    change = row['涨跌幅']
                    volume = row['成交量']
                    amount = row['成交额']
                    amplitude = row['振幅']
                    high = row['最高']
                    low = row['最低']
                    open_price = row['今开']
                    pre_close = row['昨收']
                except Exception as e2:
                    return f"❌ 查询失败: {str(e2)}"
            
            change_emoji = "📈" if change >= 0 else "📉"
            
            msg = f"{change_emoji} **{name}** ({symbol})\n\n"
            msg += f"现价: {price:.2f}\n"
            msg += f"涨跌: {change:+.2f}%\n"
            msg += f"今开: {open_price:.2f} | 昨收: {pre_close:.2f}\n"
            msg += f"最高: {high:.2f} | 最低: {low:.2f}\n"
            msg += f"振幅: {amplitude:.2f}%\n"
            msg += f"成交量: {_format_money(volume)}\n"
            msg += f"成交额: {_format_money(amount)}"
            
            return msg
        
        # 港股
        elif stock_type == 'hk':
            df = ak.stock_hk_spot_em()
            row = df[df['代码'] == symbol]
            if row.empty:
                return f"❌ 未找到港股: {symbol}"
            
            row = row.iloc[0]
            name = row['名称']
            price = row['最新价']
            change = row['涨跌幅']
            volume = row['成交量']
            
            change_emoji = "📈" if change >= 0 else "📉"
            
            msg = f"{change_emoji} **{name}** (港股 {symbol})\n\n"
            msg += f"现价: {price:.2f} HKD\n"
            msg += f"涨跌: {change:+.2f}%\n"
            msg += f"成交量: {_format_money(volume)}"
            
            return msg
        
        # 美股
        elif stock_type == 'us':
            df = ak.stock_us_spot_em(symbol=symbol)
            if df.empty:
                return f"❌ 未找到美股: {symbol}"
            
            row = df.iloc[0]
            name = row['名称']
            price = row['最新价']
            change = row['涨跌幅']
            
            change_emoji = "📈" if change >= 0 else "📉"
            
            msg = f"{change_emoji} **{name}** (美股 {symbol})\n\n"
            msg += f"现价: ${price:.2f}\n"
            msg += f"涨跌: {change:+.2f}%"
            
            return msg
        
    except Exception as e:
        return f"❌ 查询失败: {str(e)}"


def action_index(symbol: str = "000001") -> str:
    """
    查询指数行情
    
    Args:
        symbol: 指数代码
            - 000001: 上证指数
            - 399001: 深证成指
            - 399006: 创业板指
            - HSI: 恒生指数
            - DJI: 道琼斯
            - IXIC: 纳斯达克
            - SPX: 标普500
    
    Returns:
        指数行情信息
    """
    try:
        symbol = str(symbol).upper()
        
        # A股指数
        if symbol in ['000001', '399001', '399006']:
            df = ak.stock_zh_index_spot_em()
            
            if symbol == '000001':
                code = '000001'
                name = '上证指数'
            elif symbol == '399001':
                code = '399001'
                name = '深证成指'
            else:
                code = '399006'
                name = '创业板指'
            
            row = df[df['代码'] == code].iloc[0]
            price = row['最新价']
            change = row['涨跌幅']
            volume = row['成交量']
            amount = row['成交额']
            
            change_emoji = "📈" if change >= 0 else "📉"
            
            msg = f"{change_emoji} **{name}** ({symbol})\n\n"
            msg += f"点位: {price:.2f}\n"
            msg += f"涨跌: {change:+.2f}%\n"
            msg += f"成交量: {_format_money(volume)}\n"
            msg += f"成交额: {_format_money(amount)}"
            
            return msg
        
        # 港股指数
        elif symbol == 'HSI':
            df = ak.stock_hk_index_spot_em()
            row = df[df['指数代码'] == 'HSI'].iloc[0]
            
            name = row['指数名称']
            price = row['最新点位']
            change = row['涨跌幅']
            
            change_emoji = "📈" if change >= 0 else "📉"
            
            msg = f"{change_emoji} **{name}** (恒生指数)\n\n"
            msg += f"点位: {price:.2f}\n"
            msg += f"涨跌: {change:+.2f}%"
            
            return msg
        
        # 美股指数
        elif symbol in ['DJI', 'IXIC', 'SPX']:
            df = ak.stock_us_index_spot_em()
            
            if symbol == 'DJI':
                name = '道琼斯工业指数'
                row = df[df['指数名称'] == name].iloc[0]
            elif symbol == 'IXIC':
                name = '纳斯达克综合指数'
                row = df[df['指数名称'] == name].iloc[0]
            else:
                name = '标普500指数'
                row = df[df['指数名称'] == name].iloc[0]
            
            price = row['最新点位']
            change = row['涨跌幅']
            
            change_emoji = "📈" if change >= 0 else "📉"
            
            msg = f"{change_emoji} **{name}** ({symbol})\n\n"
            msg += f"点位: {price:.2f}\n"
            msg += f"涨跌: {change:+.2f}%"
            
            return msg
        
        else:
            return f"❌ 不支持的指数代码: {symbol}\n支持的指数: 000001(上证), 399001(深证), 399006(创业板), HSI(恒生), DJI(道琼斯), IXIC(纳斯达克), SPX(标普500)"
    
    except Exception as e:
        return f"❌ 查询失败: {str(e)}"


def action_fund(code: str) -> str:
    """
    查询基金净值
    
    Args:
        code: 基金代码
    
    Returns:
        基金信息
    """
    try:
        df = ak.fund_em_fund_spot(code=code)
        
        if df.empty:
            return f"❌ 未找到基金: {code}"
        
        row = df.iloc[0]
        name = row['基金名称']
        net_value = row['单位净值']
        acc_value = row['累计净值']
        change = row['日增长率']
        
        change_emoji = "📈" if change >= 0 else "📉"
        
        msg = f"📊 **{name}** ({code})\n\n"
        msg += f"单位净值: {net_value:.4f}\n"
        msg += f"累计净值: {acc_value:.4f}\n"
        msg += f"日增长: {change_emoji} {change:+.2f}%"
        
        return msg
    
    except Exception as e:
        return f"❌ 查询失败: {str(e)}"


def action_news(count: int = 10) -> str:
    """
    获取财经新闻
    
    Args:
        count: 新闻数量，默认10条
    
    Returns:
        财经新闻列表
    """
    try:
        df = ak.stock_news_em()
        
        msg = "📰 **财经新闻**\n\n"
        
        for i, row in df.head(count).iterrows():
            title = row['新闻标题'][:40]
            if len(row['新闻标题']) > 40:
                title += '...'
            time = row['发布时间']
            msg += f"{i+1}. {title}\n   {time}\n\n"
        
        return msg.strip()
    
    except Exception as e:
        return f"❌ 获取新闻失败: {str(e)}"


def action_help() -> str:
    """帮助信息"""
    return """# 股票咨询查询使用指南

## 查询股票行情:
stock(action="quote", symbol="600519")  # 茅台
stock(action="quote", symbol="000001")  # 平安银行
stock(action="quote", symbol="00700")   # 腾讯控股(港股)
stock(action="quote", symbol="AAPL")    # 苹果(美股)

## 查询指数:
stock(action="index", symbol="000001")  # 上证指数
stock(action="index", symbol="399001")  # 深证成指
stock(action="index", symbol="399006")  # 创业板指
stock(action="index", symbol="HSI")      # 恒生指数
stock(action="index", symbol="DJI")      # 道琼斯
stock(action="index", symbol="IXIC")     # 纳斯达克
stock(action="index", symbol="SPX")      # 标普500

## 查询基金净值:
stock(action="fund", code="110022")

## 查询财经新闻:
stock(action="news", count=10)

## 支持的市场:
- A股: 6位数字代码（上证6开头，深证0/3开头）
- 港股: 5位数字代码
- 美股: 字母代码（AAPL、MSFT等）"""


def run(action: str = "help", **kwargs) -> str:
    """
    主运行函数
    
    Args:
        action: 操作类型 (quote/index/fund/news/help)
        **kwargs: 其他参数
    
    Returns:
        操作结果
    """
    action_map = {
        "quote": lambda: action_quote(
            symbol=kwargs.get("symbol", "")
        ),
        "index": lambda: action_index(
            symbol=kwargs.get("symbol", "000001")
        ),
        "fund": lambda: action_fund(
            code=kwargs.get("code", "")
        ),
        "news": lambda: action_news(
            count=kwargs.get("count", 10)
        ),
        "help": action_help
    }
    
    if action not in action_map:
        return f"❌ 未知操作: {action}\n\n{action_help()}"
    
    return action_map[action]()


if __name__ == "__main__":
    # 测试
    print(run("help"))
