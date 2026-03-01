"""
记账理财小助手 - accounting skill
帮助用户管理个人财务，记录收支情况，提供统计分析和建议。
"""

import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Dict, List, Any

# 数据目录
DATA_DIR = Path("D:/Code/nanobot-xiao/.workspace/data/accounting")
RECORDS_FILE = DATA_DIR / "records.json"
BUDGET_FILE = DATA_DIR / "budget.json"
PROFILE_FILE = DATA_DIR / "profile.json"

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 支出分类
EXPENSE_CATEGORIES = [
    "餐饮", "交通", "购物", "娱乐", "住房", 
    "医疗", "教育", "投资", "保险", "其他"
]

# 收入来源
INCOME_SOURCES = ["工资", "奖金", "兼职", "投资收益", "退款", "其他"]


def _load_json(file_path: Path, default: Any = None) -> Any:
    """加载JSON文件"""
    if default is None:
        default = []
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default
    return default


def _save_json(file_path: Path, data: Any):
    """保存JSON文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_records() -> List[Dict]:
    """加载收支记录"""
    return _load_json(RECORDS_FILE, [])


def _save_records(records: List[Dict]):
    """保存收支记录"""
    _save_json(RECORDS_FILE, records)


def _load_budget() -> Dict:
    """加载预算配置"""
    return _load_json(BUDGET_FILE, {"total": 0, "categories": {}})


def _save_budget(budget: Dict):
    """保存预算配置"""
    _save_json(BUDGET_FILE, budget)


def _load_profile() -> Dict:
    """加载用户财务档案"""
    return _load_json(PROFILE_FILE, {
        "fixed_income": 0,
        "other_income": 0,
        "created_at": datetime.now().isoformat()
    })


def _save_profile(profile: Dict):
    """保存用户财务档案"""
    _save_json(PROFILE_FILE, profile)


def action_income(amount: float, source: str = "其他", note: str = "") -> str:
    """
    记录收入
    
    Args:
        amount: 收入金额
        source: 收入来源（工资/奖金/兼职/投资收益/退款/其他）
        note: 备注
    
    Returns:
        操作结果消息
    """
    records = _load_records()
    
    record = {
        "type": "income",
        "amount": amount,
        "source": source,
        "note": note,
        "date": date.today().isoformat(),
        "datetime": datetime.now().isoformat()
    }
    
    records.append(record)
    _save_records(records)
    
    return f"✅ 已记录收入：{amount:.2f}元 (来源: {source})"


def action_expense(amount: float, category: str = "其他", note: str = "") -> str:
    """
    记录支出
    
    Args:
        amount: 支出金额
        category: 支出分类（餐饮/交通/购物/娱乐/住房/医疗/教育/投资/保险/其他）
        note: 备注
    
    Returns:
        操作结果消息
    """
    if category not in EXPENSE_CATEGORIES:
        category = "其他"
    
    records = _load_records()
    
    record = {
        "type": "expense",
        "amount": amount,
        "category": category,
        "note": note,
        "date": date.today().isoformat(),
        "datetime": datetime.now().isoformat()
    }
    
    records.append(record)
    _save_records(records)
    
    return f"✅ 已记录支出：{amount:.2f}元 (分类: {category})"


def action_today() -> str:
    """查看今日统计"""
    today = date.today().isoformat()
    records = _load_records()
    
    today_records = [r for r in records if r.get("date") == today]
    
    income = sum(r["amount"] for r in today_records if r["type"] == "income")
    expenses = sum(r["amount"] for r in today_records if r["type"] == "expense")
    
    # 分类统计
    category_stats = {}
    for r in today_records:
        if r["type"] == "expense":
            cat = r.get("category", "其他")
            category_stats[cat] = category_stats.get(cat, 0) + r["amount"]
    
    # 构建消息
    msg = f"📊 **今日收支统计** ({today})\n\n"
    msg += f"💰 收入: {income:.2f}元\n"
    msg += f"💸 支出: {expenses:.2f}元\n"
    msg += f"📈 结余: {income - expenses:.2f}元\n"
    
    if category_stats:
        msg += "\n**支出分类:**\n"
        for cat, amt in sorted(category_stats.items(), key=lambda x: -x[1]):
            pct = (amt / expenses * 100) if expenses > 0 else 0
            msg += f"  • {cat}: {amt:.2f}元 ({pct:.1f}%)\n"
    
    # 预算对比
    budget = _load_budget()
    if budget.get("total", 0) > 0:
        daily_budget = budget["total"] / 30
        if expenses > daily_budget:
            msg += f"\n⚠️ 今日支出已超过日均预算({daily_budget:.0f}元)"
    
    return msg


def action_month(year: int = None, month: int = None) -> str:
    """查看月度统计"""
    if year is None or month is None:
        today = date.today()
        year, month = today.year, today.month
    
    records = _load_records()
    
    month_str = f"{year}-{month:02d}"
    month_records = [r for r in records if r.get("date", "").startswith(month_str)]
    
    income = sum(r["amount"] for r in month_records if r["type"] == "income")
    expenses = sum(r["amount"] for r in month_records if r["type"] == "expense")
    
    # 分类统计
    category_stats = {}
    for r in month_records:
        if r["type"] == "expense":
            cat = r.get("category", "其他")
            category_stats[cat] = category_stats.get(cat, 0) + r["amount"]
    
    # 构建消息
    msg = f"📊 **月度收支统计** ({year}年{month}月)\n\n"
    msg += f"💰 收入: {income:.2f}元\n"
    msg += f"💸 支出: {expenses:.2f}元\n"
    msg += f"📈 结余: {income - expenses:.2f}元\n"
    
    if category_stats:
        msg += "\n**支出分类:**\n"
        for cat, amt in sorted(category_stats.items(), key=lambda x: -x[1]):
            pct = (amt / expenses * 100) if expenses > 0 else 0
            msg += f"  • {cat}: {amt:.2f}元 ({pct:.1f}%)\n"
    
    # 预算对比
    budget = _load_budget()
    if budget.get("total", 0) > 0:
        if expenses > budget["total"]:
            msg += f"\n⚠️ 已超预算！超支 {expenses - budget['total']:.2f}元"
        else:
            msg += f"\n💡 预算剩余: {budget['total'] - expenses:.2f}元"
    
    # 理财建议
    msg += "\n**💡 理财建议:**\n"
    if expenses > income * 0.8:
        msg += "• 支出占比过高，建议控制开支\n"
    elif expenses < income * 0.5:
        msg += "• 储蓄率良好，建议考虑投资理财\n"
    else:
        msg += "• 收支平衡，建议建立应急储备\n"
    
    # 检查是否有大额支出
    if category_stats:
        max_cat = max(category_stats.items(), key=lambda x: x[1])
        msg += f"• 最大支出类别是{max_cat[0]}，注意控制\n"
    
    return msg


def action_budget(total: float = 0, categories: Dict[str, float] = None) -> str:
    """
    设置预算
    
    Args:
        total: 总预算
        categories: 分类预算 {"餐饮": 1000, "交通": 500}
    """
    budget = {
        "total": total,
        "categories": categories or {},
        "updated_at": datetime.now().isoformat()
    }
    _save_budget(budget)
    
    msg = f"✅ 已设置月度预算: {total:.2f}元\n"
    if categories:
        msg += "\n**分类预算:**\n"
        for cat, amt in categories.items():
            msg += f"  • {cat}: {amt:.2f}元\n"
    
    return msg


def action_profile() -> str:
    """查看财务档案"""
    profile = _load_profile()
    budget = _load_budget()
    
    msg = "👤 **财务档案**\n\n"
    msg += f"固定收入: {profile.get('fixed_income', 0):.2f}元/月\n"
    msg += f"其他收入: {profile.get('other_income', 0):.2f}元/月\n"
    msg += f"月预算: {budget.get('total', 0):.2f}元\n"
    
    total_income = profile.get('fixed_income', 0) + profile.get('other_income', 0)
    if total_income > 0 and budget.get('total', 0) > 0:
        savings_rate = (total_income - budget['total']) / total_income * 100
        msg += f"\n目标储蓄率: {savings_rate:.1f}%"
    
    return msg


def action_set_income(fixed_income: float = 0, other_income: float = 0) -> str:
    """
    设置收入信息
    
    Args:
        fixed_income: 固定收入（月薪等）
        other_income: 其他收入（兼职、投资等）
    """
    profile = _load_profile()
    profile["fixed_income"] = fixed_income
    profile["other_income"] = other_income
    profile["updated_at"] = datetime.now().isoformat()
    
    _save_profile(profile)
    
    total = fixed_income + other_income
    return f"✅ 已设置收入信息\n\n💰 固定收入: {fixed_income:.2f}元/月\n💵 其他收入: {other_income:.2f}元/月\n📊 月总收入: {total:.2f}元"


def action_help() -> str:
    """帮助信息"""
    return """# 记账理财小助手使用指南

## 记录收入:
accounting(action="income", amount=金额, source="来源", note="备注")

## 记录支出:
accounting(action="expense", amount=金额, category="分类", note="备注")

## 查看今日统计:
accounting(action="today")

## 查看月度统计:
accounting(action="month")

## 设置预算:
accounting(action="budget", total=总预算, categories={"分类": 金额})

## 查看财务档案:
accounting(action="profile")

## 设置收入:
accounting(action="set_income", fixed_income=固定收入, other_income=其他收入)

## 支出分类: 餐饮、交通、购物、娱乐、住房、医疗、教育、投资、保险、其他
## 收入来源: 工资、奖金、兼职、投资收益、退款、其他"""


def run(action: str = "help", **kwargs) -> str:
    """
    主运行函数
    
    Args:
        action: 操作类型 (income/expense/today/month/budget/profile/set_income/help)
        **kwargs: 其他参数
    
    Returns:
        操作结果消息
    """
    action_map = {
        "income": lambda: action_income(
            amount=kwargs.get("amount", 0),
            source=kwargs.get("source", "其他"),
            note=kwargs.get("note", "")
        ),
        "expense": lambda: action_expense(
            amount=kwargs.get("amount", 0),
            category=kwargs.get("category", "其他"),
            note=kwargs.get("note", "")
        ),
        "today": action_today,
        "month": lambda: action_month(
            year=kwargs.get("year"),
            month=kwargs.get("month")
        ),
        "budget": lambda: action_budget(
            total=kwargs.get("total", 0),
            categories=kwargs.get("categories")
        ),
        "profile": action_profile,
        "set_income": lambda: action_set_income(
            fixed_income=kwargs.get("fixed_income", 0),
            other_income=kwargs.get("other_income", 0)
        ),
        "help": action_help
    }
    
    if action not in action_map:
        return f"❌ 未知操作: {action}\n\n{action_help()}"
    
    return action_map[action]()


if __name__ == "__main__":
    # 测试
    print(run("help"))
