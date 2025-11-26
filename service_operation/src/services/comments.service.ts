import { Comment } from '../models/comment.model';
import { Post } from '../models/post.model';
import { Reaction } from '../models/reaction.model';
import {
  CommentCreateInput,
  CommentUpdateInput,
  CommentResponse,
  CommentQueryParams,
} from '../types';
import { parsePaginationParams, applySorting, applyPagination } from '../utils/pagination.util';

/**
 * Comments Service - Business logic for comments
 */
class CommentsService {
  /**
   * Get all comments for a post
   */
  async getComments(
    postId: string,
    queryParams: CommentQueryParams
  ): Promise<{ comments: CommentResponse[]; total?: number }> {
    const paginationInfo = parsePaginationParams(queryParams);
    const { user_id } = queryParams;

    // Build filter query
    const filter: any = { post_id: postId };

    if (user_id) {
      filter.user_id = user_id;
    }

    // Build query
    let query = Comment.find(filter);

    // Apply sorting (newest first by default)
    query = applySorting(query, 'created_at', 'desc');

    // Apply pagination
    query = applyPagination(query, paginationInfo);

    // Execute query
    const comments = await query.lean().exec();

    // Get total count for pagination metadata
    let total: number | undefined;
    if (!paginationInfo.cursor) {
      total = await Comment.countDocuments(filter);
    }

    return {
      comments: comments.map(this.formatCommentResponse),
      total,
    };
  }

  /**
   * Get a single comment by ID
   */
  async getCommentById(postId: string, commentId: string): Promise<CommentResponse | null> {
    const comment = await Comment.findOne({ _id: commentId, post_id: postId }).lean().exec();
    return comment ? this.formatCommentResponse(comment) : null;
  }

  /**
   * Create a new comment
   */
  async createComment(
    userId: string,
    postId: string,
    data: CommentCreateInput
  ): Promise<CommentResponse> {
    const comment = await Comment.create({
      ...data,
      user_id: userId,
      post_id: postId,
    });

    // Increment parent comment's reply count if it's a reply
    if (data.parent_id) {
      await Comment.findByIdAndUpdate(data.parent_id, { $inc: { replies_count: 1 } });
    }

    // Increment post's comment count
    await Post.findByIdAndUpdate(postId, { $inc: { comments_count: 1 } });

    return this.formatCommentResponse(comment.toObject());
  }

  /**
   * Update a comment
   */
  async updateComment(
    commentId: string,
    userId: string,
    postId: string,
    data: CommentUpdateInput
  ): Promise<CommentResponse | null> {
    const comment = await Comment.findOneAndUpdate(
      { _id: commentId, user_id: userId, post_id: postId },
      { $set: data },
      { new: true, runValidators: true }
    ).lean().exec();

    return comment ? this.formatCommentResponse(comment) : null;
  }

  /**
   * Delete a comment
   */
  async deleteComment(commentId: string, userId: string, postId: string): Promise<boolean> {
    const comment = await Comment.findOne({ _id: commentId, post_id: postId });

    if (!comment || comment.user_id !== userId) {
      return false;
    }

    const result = await Comment.deleteOne({ _id: commentId, user_id: userId });

    if (result.deletedCount > 0) {
      // Decrement parent comment's reply count if it's a reply
      if (comment.parent_id) {
        await Comment.findByIdAndUpdate(comment.parent_id, { $inc: { replies_count: -1 } });
      }

      // Decrement post's comment count
      await Post.findByIdAndUpdate(postId, { $inc: { comments_count: -1 } });

      // Clean up associated reactions
      await Reaction.deleteMany({ target_id: commentId, target_type: 'comment' });

      return true;
    }

    return false;
  }

  /**
   * Check if comment exists
   */
  async commentExists(commentId: string): Promise<boolean> {
    const count = await Comment.countDocuments({ _id: commentId });
    return count > 0;
  }

  /**
   * Increment reaction count
   */
  async incrementReactionCount(commentId: string): Promise<void> {
    await Comment.findByIdAndUpdate(commentId, { $inc: { likes_count: 1 } });
  }

  /**
   * Decrement reaction count
   */
  async decrementReactionCount(commentId: string): Promise<void> {
    await Comment.findByIdAndUpdate(commentId, { $inc: { likes_count: -1 } });
  }

  /**
   * Format comment for response
   */
  private formatCommentResponse(comment: any): CommentResponse {
    return {
      id: comment._id.toString(),
      user_id: comment.user_id,
      post_id: comment.post_id,
      parent_id: comment.parent_id,
      content: comment.content,
      media_ids: comment.media_ids,
      tags: comment.tags,
      likes_count: comment.likes_count,
      replies_count: comment.replies_count,
      created_at: comment.created_at?.toISOString() || new Date().toISOString(),
      updated_at: comment.updated_at?.toISOString() || new Date().toISOString(),
    };
  }
}

export default new CommentsService();
