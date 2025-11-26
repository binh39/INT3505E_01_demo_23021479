import { Reaction } from '../models/reaction.model';
import {
  ReactionUpsertInput,
  ReactionResponse,
  ReactionQueryParams,
  TargetType,
} from '../types';
import { parsePaginationParams, applySorting, applyPagination } from '../utils/pagination.util';

/**
 * Reactions Service - Business logic for reactions
 */
class ReactionsService {
  /**
   * Get all reactions for a target (post or comment)
   */
  async getReactions(
    targetId: string,
    targetType: TargetType,
    queryParams: ReactionQueryParams
  ): Promise<{ reactions: ReactionResponse[]; total?: number }> {
    const paginationInfo = parsePaginationParams(queryParams);
    const { react_type } = queryParams;

    // Build filter query
    const filter: any = {
      target_id: targetId,
      target_type: targetType,
    };

    if (react_type) {
      filter.react_type = react_type;
    }

    // Build query
    let query = Reaction.find(filter);

    // Apply sorting (newest first by default)
    query = applySorting(query, 'created_at', 'desc');

    // Apply pagination
    query = applyPagination(query, paginationInfo);

    // Execute query
    const reactions = await query.lean().exec();

    // Get total count for pagination metadata
    let total: number | undefined;
    if (!paginationInfo.cursor) {
      total = await Reaction.countDocuments(filter);
    }

    return {
      reactions: reactions.map(this.formatReactionResponse),
      total,
    };
  }

  /**
   * Upsert a reaction (create or update)
   */
  async upsertReaction(
    userId: string,
    targetId: string,
    targetType: TargetType,
    data: ReactionUpsertInput
  ): Promise<{ reaction: ReactionResponse; isNew: boolean }> {
    const existingReaction = await Reaction.findOne({
      user_id: userId,
      target_id: targetId,
      target_type: targetType,
    });

    if (existingReaction) {
      // Update existing reaction
      existingReaction.react_type = data.react_type;
      await existingReaction.save();

      return {
        reaction: this.formatReactionResponse(existingReaction.toObject()),
        isNew: false,
      };
    } else {
      // Create new reaction
      const reaction = await Reaction.create({
        user_id: userId,
        target_id: targetId,
        target_type: targetType,
        react_type: data.react_type,
      });

      return {
        reaction: this.formatReactionResponse(reaction.toObject()),
        isNew: true,
      };
    }
  }

  /**
   * Delete a reaction
   */
  async deleteReaction(
    userId: string,
    targetId: string,
    targetType: TargetType
  ): Promise<boolean> {
    const result = await Reaction.deleteOne({
      user_id: userId,
      target_id: targetId,
      target_type: targetType,
    });

    return result.deletedCount > 0;
  }

  /**
   * Check if user has reacted to target
   */
  async hasUserReacted(userId: string, targetId: string, targetType: TargetType): Promise<boolean> {
    const count = await Reaction.countDocuments({
      user_id: userId,
      target_id: targetId,
      target_type: targetType,
    });
    return count > 0;
  }

  /**
   * Format reaction for response
   */
  private formatReactionResponse(reaction: any): ReactionResponse {
    return {
      id: reaction._id.toString(),
      user_id: reaction.user_id,
      target_id: reaction.target_id,
      target_type: reaction.target_type,
      react_type: reaction.react_type,
      created_at: reaction.created_at?.toISOString() || new Date().toISOString(),
      updated_at: reaction.updated_at?.toISOString() || new Date().toISOString(),
    };
  }
}

export default new ReactionsService();
