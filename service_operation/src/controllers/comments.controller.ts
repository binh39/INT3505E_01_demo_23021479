import { Response, NextFunction } from 'express';
import { AuthRequest } from '../types';
import commentsService from '../services/comments.service';
import postsService from '../services/posts.service';
import {
  sendSuccess,
  sendError,
  generateCommentLinks,
  generateCommentsCollectionLinks,
} from '../utils/response.util';
import { buildPaginationMetadata } from '../utils/pagination.util';

/**
 * Comments Controller - Request handlers for comment endpoints
 */
class CommentsController {
  /**
   * GET /posts/:post_id/comments - Get all comments for a post
   */
  async getComments(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
    try {
      const { post_id } = req.params;

      // Check if post exists
      const postExists = await postsService.postExists(post_id);
      if (!postExists) {
        sendError(res, 'RESOURCE_NOT_FOUND', 'Post not found', 404);
        return;
      }

      const { comments, total } = await commentsService.getComments(post_id, req.query);

      const paginationInfo = buildPaginationMetadata(
        parseInt(String(req.query.limit || '20'), 10),
        parseInt(String(req.query.offset || '0'), 10),
        total
      );

      sendSuccess(
        res,
        comments,
        200,
        'Comments retrieved successfully',
        generateCommentsCollectionLinks(post_id, req.query),
        { pagination: paginationInfo }
      );
    } catch (error) {
      next(error);
    }
  }

  /**
   * GET /posts/:post_id/comments/:comment_id - Get single comment
   */
  async getCommentById(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
    try {
      const { post_id, comment_id } = req.params;

      const comment = await commentsService.getCommentById(post_id, comment_id);

      if (!comment) {
        sendError(res, 'RESOURCE_NOT_FOUND', 'Comment not found', 404);
        return;
      }

      sendSuccess(
        res,
        comment,
        200,
        'Comment retrieved successfully',
        generateCommentLinks(post_id, comment_id)
      );
    } catch (error) {
      next(error);
    }
  }

  /**
   * POST /posts/:post_id/comments - Create new comment
   */
  async createComment(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
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

      const comment = await commentsService.createComment(userId, post_id, req.body);

      sendSuccess(
        res,
        comment,
        201,
        'Comment created successfully',
        generateCommentLinks(post_id, comment.id)
      );
    } catch (error) {
      next(error);
    }
  }

  /**
   * PATCH /posts/:post_id/comments/:comment_id - Update comment
   */
  async updateComment(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
    try {
      const userId = req.user?.id;
      const { post_id, comment_id } = req.params;

      if (!userId) {
        sendError(res, 'AUTH_REQUIRED', 'User authentication required', 401);
        return;
      }

      const comment = await commentsService.updateComment(comment_id, userId, post_id, req.body);

      if (!comment) {
        sendError(res, 'PERMISSION_DENIED', 'Comment not found or access denied', 403);
        return;
      }

      sendSuccess(
        res,
        comment,
        200,
        'Comment updated successfully',
        generateCommentLinks(post_id, comment_id)
      );
    } catch (error) {
      next(error);
    }
  }

  /**
   * DELETE /posts/:post_id/comments/:comment_id - Delete comment
   */
  async deleteComment(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
    try {
      const userId = req.user?.id;
      const { post_id, comment_id } = req.params;

      if (!userId) {
        sendError(res, 'AUTH_REQUIRED', 'User authentication required', 401);
        return;
      }

      const deleted = await commentsService.deleteComment(comment_id, userId, post_id);

      if (!deleted) {
        sendError(res, 'PERMISSION_DENIED', 'Comment not found or access denied', 403);
        return;
      }

      res.status(204).send();
    } catch (error) {
      next(error);
    }
  }
}

export default new CommentsController();
