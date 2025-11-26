import { Document } from 'mongoose';

export type ReactionType = 'like' | 'love' | 'haha' | 'wow' | 'sad' | 'angry';
export type TargetType = 'post' | 'comment';

export interface IReaction extends Document {
  user_id: string;
  target_id: string;
  target_type: TargetType;
  react_type: ReactionType;
  created_at: Date;
  updated_at: Date;
}

export interface ReactionUpsertInput {
  react_type: ReactionType;
}

export interface ReactionResponse {
  id: string;
  user_id: string;
  target_id: string;
  target_type: TargetType;
  react_type: ReactionType;
  created_at: string;
  updated_at: string;
}
