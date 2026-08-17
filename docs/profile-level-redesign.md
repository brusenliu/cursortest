# 个人信息页等级系统改版 — UI 规格文档

## 1. 概述

在现有「我的」侧边栏基础上，新增角色等级、经验值、等级徽章及升级奖励红点提示，参考传统 RPG 个人信息页的信息层级。

**方案图：**

| 页面 | 文件 |
|------|------|
| **排版方案对比（5 套）** | [`mockups/layout-comparison-all.png`](../mockups/layout-comparison-all.png) · [`docs/layout-options.md`](layout-options.md) |
| 主界面（侧边栏，方案 A） | [`mockups/profile-main-mockup.png`](../mockups/profile-main-mockup.png) |
| 等级奖励面板 | [`mockups/profile-reward-panel-mockup.png`](../mockups/profile-reward-panel-mockup.png) |
| 可交互原型 | [`prototype/index.html`](../prototype/index.html) |
| 排版对比页 | [`prototype/layout-comparison.html`](../prototype/layout-comparison.html) |

---

## 2. 信息架构

```
货币栏（不变）
  ↓
身份区（头像 + 等级徽章 + 昵称 + handle）
  ↓
成长区（EXP 进度条，可点击）
  ↓
状态区（饱食度 / 幸福度，压缩样式）
  ↓
功能菜单（新增「等级奖励」入口）
```

---

## 3. 色彩规范

| 用途 | 色值 | 说明 |
|------|------|------|
| 面板背景 | `#1A1A2E` @ 85% 透明度 | 侧边栏主背景 |
| 卡片背景 | `#2A2A3E` | 菜单分组卡片 |
| 卡片悬停 | `#353550` | 菜单项 hover |
| 主文字 | `#FFFFFF` | 昵称、菜单文字 |
| 次要文字 | `#8E8E93` | @handle、未达成状态 |
| 强调色 | `#7B61FF` | 按钮、经验条起始色 |
| 强调色渐变终点 | `#B06CFF` | 经验条、领取按钮 |
| 红点 | `#FF3B30` | 通知圆点 |
| 红点描边 | `#1A1A2E` | 2dp 描边，与背景分离 |
| 饱食度条 | `#4A4A5A` / 空 `#2A2A3E` | 灰色进度 |
| 幸福度条 | `#FF6B9D` / 空 `#2A2A3E` | 粉色进度 |
| 已领取 | `#34C759` | 绿色勾选态 |
| 未达成 | `#5A5A6A` | 灰色锁定 |

---

## 4. 字体规范

| 元素 | 字号 | 字重 | 颜色 |
|------|------|------|------|
| 昵称 | 18sp | Bold (700) | `#FFFFFF` |
| @handle | 13sp | Regular (400) | `#8E8E93` |
| 等级徽章数字 | 14sp | Bold (700) | `#FFFFFF` |
| EXP 数值 | 12sp | Medium (500) | `#B06CFF` |
| 状态标签 | 12sp | Regular (400) | `#AAAAAA` |
| 状态数值 | 12sp | Medium (500) | `#FFFFFF` |
| 菜单项 | 15sp | Regular (400) | `#FFFFFF` |
| 奖励面板标题 | 17sp | Bold (700) | `#FFFFFF` |
| 里程碑等级 | 14sp | Bold (700) | `#FFFFFF` |
| 奖励描述 | 13sp | Regular (400) | `#AAAAAA` |

---

## 5. 尺寸与间距

### 5.1 身份区

| 元素 | 尺寸 |
|------|------|
| 头像 | 64 × 64 dp，圆角 12dp |
| 等级徽章胶囊 | 高度 28–32dp，内边距左右 10dp |
| 徽章图标 | 20 × 20dp |
| 红点 | 直径 8dp，位于徽章右上角 offset (-2, -2) |
| 头像 ↔ 文字区间距 | 12dp |
| 昵称 ↔ handle 间距 | 2dp |
| 身份区 ↔ EXP 条间距 | 12dp |

### 5.2 经验条

| 元素 | 尺寸 |
|------|------|
| 进度条高度 | 6–8dp，全圆角 |
| 进度条宽度 | 面板内容区 100% |
| EXP 文字 | 右对齐或条下方，12sp |
| EXP 条 ↔ 状态区间距 | 16dp |

### 5.3 状态区（压缩）

| 元素 | 尺寸 |
|------|------|
| 进度条高度 | 4dp |
| 行高 | 28dp |
| 图标 | 16 × 16dp |
| 两行间距 | 8dp |

### 5.4 菜单

| 元素 | 尺寸 |
|------|------|
| 菜单项高度 | 48dp |
| 卡片圆角 | 12dp |
| 卡片内边距 | 4dp |
| 卡片组间距 | 8dp |
| 菜单图标 | 20 × 20dp |
| 菜单红点 | 8dp，右对齐 offset 16dp |

---

## 6. 等级徽章映射

10 档徽章资源，按当前等级区间自动切换：

| Tier | 等级区间 | 徽章形态 | 资源文件名 |
|------|---------|---------|-----------|
| 01 | Lv.1 – 10 | 绿色倒三角 | `level_badge_tier_01@2x.png` |
| 02 | Lv.11 – 20 | 青色菱形 | `level_badge_tier_02@2x.png` |
| 03 | Lv.21 – 30 | 蓝色五边形 | `level_badge_tier_03@2x.png` |
| 04 | Lv.31 – 40 | 紫色六边形 | `level_badge_tier_04@2x.png` |
| 05 | Lv.41 – 50 | 粉色六边形 | `level_badge_tier_05@2x.png` |
| 06 | Lv.51 – 60 | 亮紫六边形 | `level_badge_tier_06@2x.png` |
| 07 | Lv.61 – 70 | 带翼金色边框 | `level_badge_tier_07@2x.png` |
| 08 | Lv.71 – 80 | 华丽紫金翼 | `level_badge_tier_08@2x.png` |
| 09 | Lv.81 – 90 | 大型金翼 | `level_badge_tier_09@2x.png` |
| 10 | Lv.91+ | 彩虹渐变顶级 | `level_badge_tier_10@2x.png` |

### 映射算法

```typescript
function getBadgeTier(level: number): number {
  if (level >= 91) return 10;
  return Math.floor((level - 1) / 10) + 1;
}
```

徽章胶囊内显示 **当前实际等级数字**（如 Lv.35 显示 `35`），图标使用对应 tier 的图形。

---

## 7. 红点规则

### 7.1 显示条件

```typescript
showRedDot = pendingLevelRewards.length > 0;
```

### 7.2 显示位置

| 位置 | 条件 |
|------|------|
| 等级徽章右上角 | `showRedDot === true` |
| 「等级奖励」菜单项右侧 | `showRedDot === true` |
| 奖励面板内「领取」按钮 | 该行奖励状态为 `claimable` |

### 7.3 状态机

```
无待领奖励 ──升级到达里程碑──→ 有待领奖励
有待领奖励 ──领取全部可领奖励──→ 无待领奖励
有待领奖励 ──领取部分──→ 有待领奖励（仍有未领）
```

### 7.4 里程碑间隔

建议 **每 5 级** 设奖励节点，徽章换档（Lv.11/21/31…）时附加档位奖励：

| 里程碑 | 建议奖励 |
|--------|---------|
| Lv.5 | 金币 × 200 |
| Lv.10 | 金币 × 500 |
| Lv.11 | 档位奖励：钻石 × 30 |
| Lv.15 | 金币 × 800 |
| Lv.20 | 装扮 × 1 |
| Lv.21 | 档位奖励：钻石 × 50 |
| … | 依此类推 |

---

## 8. 交互说明

### 8.1 入口（三处等价）

| 入口 | 行为 |
|------|------|
| 等级徽章 | 点击 → 打开等级奖励面板 |
| EXP 进度条 | 点击 → 打开等级奖励面板 |
| 「等级奖励」菜单项 | 点击 → 打开等级奖励面板 |

### 8.2 等级奖励面板

| 元素 | 行为 |
|------|------|
| ← 返回 | 关闭面板，回到侧边栏 |
| 里程碑列表 | 纵向滚动 |
| 「领取」按钮 | 调用领取 API，成功后刷新列表与红点 |
| 「已领取」 | 不可点击，绿色勾选 |
| 「未达成」 | 不可点击，灰色锁定 |

### 8.3 领取流程

```
用户点击「领取」
  → 请求 POST /api/level/reward/claim { level: 35 }
  → 成功：弹出奖励获得动画，更新 pendingRewards，刷新红点
  → 失败：Toast 提示错误
```

---

## 9. 数据接口

```typescript
interface UserLevelInfo {
  level: number;           // 当前等级，如 35
  currentExp: number;      // 当前经验，如 2450
  expToNextLevel: number;  // 升级所需经验，如 3000
  badgeTier: number;       // 1-10，由 level 计算
  pendingRewards: LevelReward[];
}

interface LevelReward {
  level: number;           // 里程碑等级
  rewards: RewardItem[];   // 奖励内容
  status: 'claimed' | 'claimable' | 'locked';
}

interface RewardItem {
  type: 'gold' | 'diamond' | 'outfit' | 'item';
  amount?: number;
  itemId?: string;
  name: string;
}
```

---

## 10. 组件结构（代码落地参考）

```
ProfileSidebar / MinePanel
├── CurrencyBar                    # 不变
├── ProfileHeader                  # 扩展
│   ├── Avatar
│   ├── LevelBadge (+ RedDot)
│   └── UserName / Handle
├── ExpProgressBar                 # 新增，可点击
├── StatusBars                     # 压缩
│   ├── HungerBar
│   └── HappinessBar
├── ProfileMenuList                # 扩展
│   ├── MenuGroup[]
│   └── MenuItem "等级奖励" (+ RedDot)
└── LevelRewardModal               # 新增
    ├── LevelSummary
    ├── ExpProgressBar
    └── MilestoneRewardList

hooks/useLevelReward.ts            # 红点与领取逻辑
constants/levelBadgeTier.ts        # 等级 → tier 映射
assets/level_badges/               # 10 档徽章 @2x/@3x
```

---

## 11. 切图清单

| 资源 | 规格 | 数量 |
|------|------|------|
| 等级徽章 tier 01–10 | PNG @2x/@3x，透明底 | 10 × 2 = 20 |
| 红点圆点 | 8dp @2x/@3x | 1 × 2 = 2 |
| EXP 条背景 | 9-patch 或 SVG | 1 |
| 菜单图标「等级奖励」 | 20dp @2x/@3x | 1 × 2 = 2 |

---

## 12. 验收标准

- [ ] 侧边栏正确展示等级徽章（数字 + 对应 tier 图标）
- [ ] EXP 进度条数值与进度一致
- [ ] 有待领奖励时，徽章和菜单项均显示红点
- [ ] 三处入口均可打开奖励面板
- [ ] 领取后红点正确消失/保留
- [ ] 未达成项灰色锁定，已领取项显示勾选
- [ ] 新增内容不破坏侧边栏滚动与原有菜单功能
- [ ] 色彩、圆角、间距与现有 UI 风格一致
