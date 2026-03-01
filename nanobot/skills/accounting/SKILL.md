---
name: accounting
description: 记账理财小助手 - 记录收支、统计分账、提供理财建议
---

# 记账理财小助手

帮助用户管理个人财务，记录收支情况，提供统计分析和建议。

## 功能

### 1. 收入/支出记录
- 记录收入（工资、奖金、投资收益等）
- 记录支出（餐饮、交通、购物、住房等）
- 自动分类（餐饮、交通、购物、娱乐、住房、医疗、教育、其他）

### 2. 每日统计
- 每日支出汇总
- 分类占比分析
- 与预算对比

### 3. 月度统计
- 月度收支汇总
- 各类支出占比
- 同比分析
- 理财建议

### 4. 预算规划
- 设置每月预算
- 各类别预算分配
- 超支提醒

## 数据存储

- 位置: `D:\Code\nanobot-xiao\.workspace\data\accounting\`
- 格式: JSON
- 文件:
  - `records.json` - 收支记录
  - `budget.json` - 预算配置
  - `profile.json` - 用户财务档案

## 使用方法

### 记录收入
```
accounting(action="income", amount=5000, source="工资", note="月工资")
```

### 记录支出
```
accounting(action="expense", amount=50, category="餐饮", note="午餐")
```

### 查看今日统计
```
accounting(action="today")
```

### 查看本月统计
```
accounting(action="month")
```

### 设置预算
```
accounting(action="budget", total=5000, categories={"餐饮":1000,"交通":500})
```

### 查看财务档案
```
accounting(action="profile")
```

### 设置收入信息
```
accounting(action="set_income", fixed_income=8000, other_income=1000)
```

## 触发定时任务

- 每天晚上8点提醒记录当天支出
- 每月1号生成上月月度报告

