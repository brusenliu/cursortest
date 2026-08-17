/**
 * 等级 → 徽章 Tier 映射
 * Tier 1 (Lv.1-10) → Tier 10 (Lv.91+)
 */
export function getBadgeTier(level: number): number {
  if (level >= 91) return 10;
  return Math.floor((level - 1) / 10) + 1;
}

export const BADGE_TIER_CONFIG = [
  { tier: 1,  levelMin: 1,  levelMax: 10,  asset: 'level_badge_tier_01', shape: 'green-triangle' },
  { tier: 2,  levelMin: 11, levelMax: 20,  asset: 'level_badge_tier_02', shape: 'cyan-diamond' },
  { tier: 3,  levelMin: 21, levelMax: 30,  asset: 'level_badge_tier_03', shape: 'blue-pentagon' },
  { tier: 4,  levelMin: 31, levelMax: 40,  asset: 'level_badge_tier_04', shape: 'purple-hexagon' },
  { tier: 5,  levelMin: 41, levelMax: 50,  asset: 'level_badge_tier_05', shape: 'pink-hexagon' },
  { tier: 6,  levelMin: 51, levelMax: 60,  asset: 'level_badge_tier_06', shape: 'bright-purple-hexagon' },
  { tier: 7,  levelMin: 61, levelMax: 70,  asset: 'level_badge_tier_07', shape: 'winged-gold-border' },
  { tier: 8,  levelMin: 71, levelMax: 80,  asset: 'level_badge_tier_08', shape: 'ornate-purple-gold-wings' },
  { tier: 9,  levelMin: 81, levelMax: 90,  asset: 'level_badge_tier_09', shape: 'large-gold-wings' },
  { tier: 10, levelMin: 91, levelMax: Infinity, asset: 'level_badge_tier_10', shape: 'rainbow-ultimate' },
] as const;

export function getBadgeAsset(level: number): string {
  const tier = getBadgeTier(level);
  return BADGE_TIER_CONFIG[tier - 1].asset;
}

export function getExpProgress(currentExp: number, expToNextLevel: number): number {
  if (expToNextLevel <= 0) return 100;
  return Math.min(100, (currentExp / expToNextLevel) * 100);
}

export function hasUnclaimedRewards(pendingRewards: { status: string }[]): boolean {
  return pendingRewards.some(r => r.status === 'claimable');
}
