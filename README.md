# 个人信息页等级系统改版

像素风社交游戏「我的」侧边栏等级系统 UI 改版方案。

## 交付物

| 文件 | 说明 |
|------|------|
| [mockups/layout-comparison-all.png](mockups/layout-comparison-all.png) | **五方案排版对比总览图** |
| [docs/layout-options.md](docs/layout-options.md) | 五方案排版说明与决策建议 |
| [prototype/layout-comparison.html](prototype/layout-comparison.html) | 五方案排版可交互对比页 |
| [mockups/profile-main-mockup.png](mockups/profile-main-mockup.png) | 主界面方案图（方案 A，含等级徽章、经验条、红点） |
| [mockups/profile-reward-panel-mockup.png](mockups/profile-reward-panel-mockup.png) | 等级奖励面板方案图 |
| [mockups/layout-scheme-b-avatar-badge.png](mockups/layout-scheme-b-avatar-badge.png) | 方案 B 高保真细节图 |
| [mockups/layout-scheme-c-ring-exp.png](mockups/layout-scheme-c-ring-exp.png) | 方案 C 高保真细节图 |
| [docs/profile-level-redesign.md](docs/profile-level-redesign.md) | 完整 UI 规格文档 |
| [prototype/index.html](prototype/index.html) | 可交互 HTML 原型（可直接浏览器打开） |
| [prototype/constants/levelBadgeTier.ts](prototype/constants/levelBadgeTier.ts) | 等级徽章映射逻辑 |
| [prototype/types/userLevel.ts](prototype/types/userLevel.ts) | 数据接口类型定义 |

## 快速预览

在浏览器中打开 `prototype/index.html` 即可体验交互原型：

- 点击等级徽章 / 经验条 / 「等级奖励」菜单 → 打开奖励面板
- 点击「领取」按钮 → 模拟领取奖励，红点自动消失
- 支持里程碑列表的已领取 / 可领取 / 未达成三种状态

## 改版要点

1. **身份区**：头像旁新增等级徽章胶囊（10 档图标 + 当前等级数字）
2. **成长区**：紫色渐变 EXP 进度条，显示当前/升级所需经验
3. **红点提示**：有待领奖励时，徽章和菜单项均显示红点
4. **等级奖励面板**：里程碑列表，支持领取/已领/未达成状态

## 接入实际项目

参考 `docs/profile-level-redesign.md` 中的组件结构与数据接口，将 `prototype/` 中的逻辑迁移至游戏前端仓库。
