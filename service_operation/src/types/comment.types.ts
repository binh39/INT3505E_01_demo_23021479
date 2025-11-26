import { Document } from 'mongoose';

export interface IComment extends Document {
  user_id: string;
  post_id: string;
  parent_id?: string;
  content: string;
  media_ids?: string[];
  tags?: string[];
  likes_count: number;
  replies_count: number;
  created_at: Date;
  updated_at: Date;
}

export interface CommentCreateInput {
  content: string;
  media_ids?: string[];
  tags?: string[];
  parent_id?: string;
}

export interface CommentUpdateInput {
  content?: string;
  media_ids?: string[];
  tags?: string[];
}

export interface CommentResponse {
  id: string;
  user_id: string;
  post_id: string;
  parent_id?: string;
  content: string;
  media_ids?: string[];
  tags?: string[];
  likes_count: number;
  replies_count: number;
  created_at: string;
  updated_at: string;
}
