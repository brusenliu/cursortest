export type RewardStatus = 'claimed' | 'claimable' | 'locked';
export type RewardType = 'gold' | 'diamond' | 'outfit' | 'item';

export interface RewardItem {
  type: RewardType;
  amount?: number;
  itemId?: string;
  name: string;
}

export interface LevelReward {
  level: number;
  rewards: RewardItem[];
  status: RewardStatus;
}

export interface UserLevelInfo {
  level: number;
  currentExp: number;
  expToNextLevel: number;
  badgeTier: number;
  pendingRewards: LevelReward[];
}

export interface LevelRewardClaimRequest {
  level: number;
}

export interface LevelRewardClaimResponse {
  success: boolean;
  claimed: RewardItem[];
  pendingRewards: LevelReward[];
}
