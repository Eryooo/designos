# [SYNTHETIC] Acme Task Manager Screenshot Notes

**状态**: SYNTHETIC / SANITIZED

## 截图概述

本文档记录 Acme Task Manager 现有界面的 synthetic screenshot notes，用于 uxeval dry-run。

## 主界面（看板视图）

- 三列布局：待办、进行中、已完成
- 每列顶部显示任务数量
- 任务卡片包含：标题、分配人头像、优先级标签

## 任务详情弹窗

- 右侧滑出
- 包含：标题、描述输入框、状态下拉、分配人选择器、优先级按钮组

## 故意制造的过程缺口（用于触发 progressive checkpoint）

**注意**: 本 notes 缺少以下关键页面状态描述：
- 空状态（无任务时的引导界面）
- 错误状态（网络失败时的提示）
- 加载状态（数据拉取中的 loading 样式）

这是故意设计的过程缺口，用于验证 progressive checkpoint 是否能捕获并触发 `continue_with_gaps` 或 `degrade_scope`。

## 成员管理界面

- 成员列表：头像、姓名、角色、操作按钮
- 邀请按钮：弹出 email 输入框

## 不包含

- 真实截图文件
- 真实 Figma / Sketch 文件链接
- 真实用户界面像素数据
- 真实设计评审记录
