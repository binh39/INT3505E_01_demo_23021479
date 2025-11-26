import mongoose, { Schema } from 'mongoose';
import { IComment } from '../types/comment.types';

const commentSchema = new Schema<IComment>(
  {
    user_id: {
      type: String,
      required: [true, 'User ID is required'],
      index: true,
    },
    post_id: {
      type: String,
      required: [true, 'Post ID is required'],
      index: true,
    },
    parent_id: {
      type: String,
      default: null,
      index: true,
    },
    content: {
      type: String,
      required: [true, 'Content is required'],
      trim: true,
      maxlength: [2000, 'Comment cannot exceed 2000 characters'],
    },
    media_ids: {
      type: [String],
      default: [],
    },
    tags: {
      type: [String],
      default: [],
    },
    likes_count: {
      type: Number,
      default: 0,
      min: 0,
    },
    replies_count: {
      type: Number,
      default: 0,
      min: 0,
    },
  },
  {
    timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' },
    versionKey: false,
  }
);

// Indexes for efficient queries
commentSchema.index({ post_id: 1, created_at: -1 });
commentSchema.index({ user_id: 1, created_at: -1 });
commentSchema.index({ parent_id: 1, created_at: -1 });

export const Comment = mongoose.model<IComment>('Comment', commentSchema);
