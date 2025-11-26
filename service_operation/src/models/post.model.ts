import mongoose, { Schema } from 'mongoose';
import { IPost } from '../types/post.types';

const postSchema = new Schema<IPost>(
  {
    user_id: {
      type: String,
      required: [true, 'User ID is required'],
      index: true,
    },
    content: {
      type: String,
      required: [true, 'Content is required'],
      trim: true,
      maxlength: [10000, 'Content cannot exceed 10000 characters'],
    },
    media_ids: {
      type: [String],
      default: [],
    },
    tags: {
      type: [String],
      default: [],
    },
    post_share_id: {
      type: String,
      default: null,
    },
    group_id: {
      type: String,
      default: null,
    },
    visibility: {
      type: String,
      enum: ['public', 'friends', 'private'],
      default: 'public',
    },
    likes_count: {
      type: Number,
      default: 0,
      min: 0,
    },
    comments_count: {
      type: Number,
      default: 0,
      min: 0,
    },
    shares_count: {
      type: Number,
      default: 0,
      min: 0,
    },
    is_moderated: {
      type: Boolean,
      default: true,
    },
  },
  {
    timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' },
    versionKey: false,
  }
);

// Indexes for efficient queries
postSchema.index({ user_id: 1, created_at: -1 });
postSchema.index({ tags: 1 });
postSchema.index({ is_moderated: 1, created_at: -1 });
postSchema.index({ visibility: 1, created_at: -1 });

// Text index for content search
postSchema.index({ content: 'text' });

export const Post = mongoose.model<IPost>('Post', postSchema);
