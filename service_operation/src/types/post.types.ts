import { Document } from 'mongoose';

export type VisibilityType = 'public' | 'friends' | 'private';

export interface IPost extends Document {
  user_id: string;
  content: string;
  media_ids?: string[];
  tags?: string[];
  post_share_id?: string;
  group_id?: string;
  visibility: VisibilityType;
  likes_count: number;
  comments_count: number;
  shares_count: number;
  is_moderated: boolean;
  created_at: Date;
  updated_at: Date;
}

export interface PostCreateInput {
  content: string;
  media_ids?: string[];
  tags?: string[];
  post_share_id?: string;
  group_id?: string;
  visibility?: VisibilityType;
}

export interface PostUpdateInput {
  content?: string;
  media_ids?: string[];
  tags?: string[];
  visibility?: VisibilityType;
}

export interface PostResponse {
  id: string;
  user_id: string;
  content: string;
  media_ids?: string[];
  tags?: string[];
  post_share_id?: string;
  group_id?: string;
  visibility: VisibilityType;
  likes_count: number;
  comments_count: number;
  shares_count: number;
  is_moderated: boolean;
  created_at: string;
  updated_at: string;
}
