import mongoose, { Schema } from 'mongoose';
import { IReaction } from '../types/reaction.types';

const reactionSchema = new Schema<IReaction>(
  {
    user_id: {
      type: String,
      required: [true, 'User ID is required'],
      index: true,
    },
    target_id: {
      type: String,
      required: [true, 'Target ID is required'],
      index: true,
    },
    target_type: {
      type: String,
      enum: ['post', 'comment'],
      required: [true, 'Target type is required'],
    },
    react_type: {
      type: String,
      enum: ['like', 'love', 'haha', 'wow', 'sad', 'angry'],
      required: [true, 'Reaction type is required'],
    },
  },
  {
    timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' },
    versionKey: false,
  }
);

// Compound unique index to ensure one user can only have one reaction per target
reactionSchema.index({ user_id: 1, target_id: 1, target_type: 1 }, { unique: true });

// Additional indexes for efficient queries
reactionSchema.index({ target_id: 1, target_type: 1, react_type: 1 });
reactionSchema.index({ user_id: 1, created_at: -1 });

export const Reaction = mongoose.model<IReaction>('Reaction', reactionSchema);
