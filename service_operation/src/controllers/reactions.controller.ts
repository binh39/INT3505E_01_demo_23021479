import { Response, NextFunction } from 'express';
import { AuthRequest } from '../types';
import reactionsService from '../services/reactions.service';
import postsService from '../services/posts.service';
import commentsService from '../services/comments.service';
import {
  sendSuccess,
  sendError,
  generateReactionsCollectionLinks,
} from '../utils/response.util';
import { buildPaginationMetadata } from '../utils/pagination.util';

/**
 * Reactions Controller - Request handlers for reaction endpoints
 */
class ReactionsController {
  /**
   * GET /posts/:post_id/reactions - Get all reactions for a post
   */
  async getPostReactions(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
    try {
      const { post_id } = req.params;

      // Check if post exists
      const postExists = await postsService.postExists(post_id);
      if (!postExists) {
        sendError(res, 'RESOURCE_NOT_FOUND', 'Post not found', 404);
        return;
      }

      const { reactions, total } = await reactionsService.getReactions(post_id, 'post', req.query);

      const paginationInfo = buildPaginationMetadata(
        parseInt(String(req.query.limit || '20'), 10),
        parseInt(String(req.query.offset || '0'), 10),
        total
      );

      sendSuccess(
        res,
        reactions,
        200,
        'Reactions retrieved successfully',
        generateReactionsCollectionLinks(post_id, 'posts'),
        { pagination: paginationInfo }
      );
    } catch (error) {
      next(error);
    }
  }

  /**
   * POST /posts/:post_id/reactions - Upsert reaction for a post
   */
  async upsertPostReaction(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
    try {
      const userId = req.user?.id;
      const { post_id } = req.params;

      if (!userId) {
        sendError(res, 'AUTH_REQUIRED', 'User authentication required', 401);
        return;
      }

      // Check if post exists
      const postExists = await postsService.postExists(post_id);
      if (!postExists) {
        sendError(res, 'RESOURCE_NOT_FOUND', 'Post not found', 404);
        return;
      }

      const { reaction, isNew } = await reactionsService.upsertReaction(
        userId,
        post_id,
        'post',
        req.body
      );

      // Update post reaction count if new reaction
      if (isNew) {
        await postsService.incrementReactionCount(post_id);
      }

      sendSuccess(
        res,
        reaction,
        200,
        isNew ? 'Reaction added successfully' : 'Reaction updated successfully',
        generateReactionsCollectionLinks(post_id, 'posts')
      );
    } catch (error) {
      next(error);
    }
  }

  /**
   * DELETE /posts/:post_id/reactions - Delete reaction from a post
   */
  async deletePostReaction(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
    try {
      const userId = req.user?.id;
      const { post_id } = req.params;

      if (!userId) {
        sendError(res, 'AUTH_REQUIRED', 'User authentication required', 401);
        return;
      }

      const deleted = await reactionsService.deleteReaction(userId, post_id, 'post');

      if (!deleted) {
        sendError(res, 'RESOURCE_NOT_FOUND', 'Reaction not found', 404);
        return;
      }

      // Update post reaction count
      await postsService.decrementReactionCount(post_id);

      res.status(204).send();
    } catch (error) {
      next(error);
    }
  }

  /**
   * GET /comments/:comment_id/reactions - Get all reactions for a comment
   */
  async getCommentReactions(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
    try {
      const { comment_id } = req.params;

      // Check if comment exists
      const commentExists = await commentsService.commentExists(comment_id);
      if (!commentExists) {
        sendError(res, 'RESOURCE_NOT_FOUND', 'Comment not found', 404);
        return;
      }

      const { reactions, total } = await reactionsService.getReactions(
        comment_id,
        'comment',
        req.query
      );

      const paginationInfo = buildPaginationMetadata(
        parseInt(String(req.query.limit || '20'), 10),
        parseInt(String(req.query.offset || '0'), 10),
        total
      );

      sendSuccess(
        res,
        reactions,
        200,
        'Reactions retrieved successfully',
        generateReactionsCollectionLinks(comment_id, 'comments'),
        { pagination: paginationInfo }
      );
    } catch (error) {
      next(error);
    }
  }

  /**
   * POST /comments/:comment_id/reactions - Upsert reaction for a comment
   */
  async upsertCommentReaction(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
    try {
      const userId = req.user?.id;
      const { comment_id } = req.params;

      if (!userId) {
        sendError(res, 'AUTH_REQUIRED', 'User authentication required', 401);
        return;
      }

      // Check if comment exists
      const commentExists = await commentsService.commentExists(comment_id);
      if (!commentExists) {
        sendError(res, 'RESOURCE_NOT_FOUND', 'Comment not found', 404);
        return;
      }

      const { reaction, isNew } = await reactionsService.upsertReaction(
        userId,
        comment_id,
        'comment',
        req.body
      );

      // Update comment reaction count if new reaction
      if (isNew) {
        await commentsService.incrementReactionCount(comment_id);
      }

      sendSuccess(
        res,
        reaction,
        200,
        isNew ? 'Reaction added successfully' : 'Reaction updated successfully',
        generateReactionsCollectionLinks(comment_id, 'comments')
      );
    } catch (error) {
      next(error);
    }
  }

  /**
   * DELETE /comments/:comment_id/reactions - Delete reaction from a comment
   */
  async deleteCommentReaction(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
    try {
      const userId = req.user?.id;
      const { comment_id } = req.params;

      if (!userId) {
        sendError(res, 'AUTH_REQUIRED', 'User authentication required', 401);
        return;
      }

      const deleted = await reactionsService.deleteReaction(userId, comment_id, 'comment');

      if (!deleted) {
        sendError(res, 'RESOURCE_NOT_FOUND', 'Reaction not found', 404);
        return;
      }

      // Update comment reaction count
      await commentsService.decrementReactionCount(comment_id);

      res.status(204).send();
    } catch (error) {
      next(error);
    }
  }
}

export default new ReactionsController();
