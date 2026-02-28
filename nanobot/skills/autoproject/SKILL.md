---
name: autoproject
description: 自动从项目清单中读取待实现功能，通过写代码/文件的方式自动实现，并报告结果。
---

# AutoProject - 自动项目实现

自动从 PROJECTS.md 清单中读取待实现功能，通过写代码/文件的方式自动实现。

## 工作流程

1. 读取 `PROJECTS.md` 待实现清单
2. 找到第一个 `pending` 状态的任务
3. 标记为 `in_progress`
4. **飞书通知用户**：即将实现的功能 + 大致计划
5. 自动实现功能（通过写代码/创建文件）
6. 标记为 `completed` 或 `failed`
7. 飞书报告实现结果

## 使用方法

### 手动触发

```
autoproject(action="run")
```

### 查看清单

```
autoproject(action="list")
```

### 添加新任务

```
autoproject(action="add", name="功能名称", description="功能描述")
```

## 清单文件

- 位置: `D:\Code\nanobot-xiao\.workspace\PROJECTS.md`
- 状态: pending / in_progress / completed / failed

## 定时自动执行

通过 cron 设置定时任务（默认已配置）：

```
# 每天凌晨 0:00
cron(action="add", cron_expr="0 0 * * *", message="自动扩展功能: 检查待实现清单", tz="Asia/Shanghai")

# 每天早上 5:00
cron(action="add", cron_expr="0 5 * * *", message="自动扩展功能: 检查待实现清单", tz="Asia/Shanghai")
```

## 实现逻辑

每个功能的"实现"方式：
1. 读取功能描述
2. 分析需要创建/修改哪些文件
3. 创建相应的代码文件（skill或tool）
4. 更新清单状态
5. 报告完成情况
