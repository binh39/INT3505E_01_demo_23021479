import { Response, NextFunction } from 'express';
import { AuthRequest } from '../types';
import postsService from '../services/posts.service';
import {
  sendSuccess,
  sendError,
  generatePostLinks,
  generatePostsCollectionLinks,
} from '../utils/response.util';
import { buildPaginationMetadata } from '../utils/pagination.util';

/**
 * Posts Controller - Request handlers for post endpoints
 */
class PostsController {
  /**
   * GET /posts - Get all posts
   */
  async getPosts(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
    try {
      const { posts, total } = await postsService.getPosts(req.query);

      const paginationInfo = buildPaginationMetadata(
        parseInt(String(req.query.limit || '20'), 10),
        parseInt(String(req.query.offset || '0'), 10),
        total
      );

      sendSuccess(
        res,
        posts,
        200,
        'Posts retrieved successfully',
        generatePostsCollectionLinks(req.query),
        { pagination: paginationInfo }
      );
    } catch (error) {
      next(error);
    }
  }

  /**
   * GET /posts/:post_id - Get single post
   */
  async getPostById(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
    try {
      const { post_id } = req.params;
      const post = await postsService.getPostById(post_id);

      if (!post) {
        sendError(res, 'RESOURCE_NOT_FOUND', 'Post not found', 404);
        return;
      }

      sendSuccess(res, post, 200, 'Post retrieved successfully', generatePostLinks(post_id));
    } catch (error) {
      next(error);
    }
  }

  /**
   * POST /posts - Create new post
   */
  async createPost(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
    try {
      const userId = req.user?.id;

      if (!userId) {
        sendError(res, 'AUTH_REQUIRED', 'User authentication required', 401);
        return;
      }

      const post = await postsService.createPost(userId, req.body);

      sendSuccess(res, post, 201, 'Post created successfully', generatePostLinks(post.id));
    } catch (error) {
      next(error);
    }
  }

  /**
   * PATCH /posts/:post_id - Update post
   */
  async updatePost(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
    try {
      const userId = req.user?.id;
      const { post_id } = req.params;

      if (!userId) {
        sendError(res, 'AUTH_REQUIRED', 'User authentication required', 401);
        return;
      }

      const post = await postsService.updatePost(post_id, userId, req.body);

      if (!post) {
        sendError(res, 'PERMISSION_DENIED', 'Post not found or access denied', 403);
        return;
      }

      sendSuccess(res, post, 200, 'Post updated successfully', generatePostLinks(post_id));
    } catch (error) {
      next(error);
    }
  }

  /**
   * DELETE /posts/:post_id - Delete post
   */
  async deletePost(req: AuthRequest, res: Response, next: NextFunction): Promise<void> {
    try {
      const userId = req.user?.id;
      const { post_id } = req.params;

      if (!userId) {
        sendError(res, 'AUTH_REQUIRED', 'User authentication required', 401);
        return;
      }

      const deleted = await postsService.deletePost(post_id, userId);

      if (!deleted) {
        sendError(res, 'PERMISSION_DENIED', 'Post not found or access denied', 403);
        return;
      }

      res.status(204).send();
    } catch (error) {
      next(error);
    }
  }
}

export default new PostsController();
