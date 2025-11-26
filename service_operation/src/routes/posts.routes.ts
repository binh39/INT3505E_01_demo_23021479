import { Router } from 'express';
import postsController from '../controllers/posts.controller';
import { authenticate, optionalAuthenticate } from '../middlewares/auth.middleware';
import { validate } from '../middlewares/validation.middleware';
import {
  createPostValidator,
  updatePostValidator,
  postIdValidator,
  getPostsQueryValidator,
} from '../validators/posts.validator';

const router = Router();

/**
 * GET /posts - Get all posts (public)
 */
router.get(
  '/',
  getPostsQueryValidator,
  validate,
  optionalAuthenticate,
  postsController.getPosts.bind(postsController)
);

/**
 * POST /posts - Create new post (authenticated)
 */
router.post(
  '/',
  createPostValidator,
  validate,
  authenticate,
  postsController.createPost.bind(postsController)
);

/**
 * GET /posts/:post_id - Get single post (public)
 */
router.get(
  '/:post_id',
  postIdValidator,
  validate,
  optionalAuthenticate,
  postsController.getPostById.bind(postsController)
);

/**
 * PATCH /posts/:post_id - Update post (authenticated)
 */
router.patch(
  '/:post_id',
  updatePostValidator,
  validate,
  authenticate,
  postsController.updatePost.bind(postsController)
);

/**
 * DELETE /posts/:post_id - Delete post (authenticated)
 */
router.delete(
  '/:post_id',
  postIdValidator,
  validate,
  authenticate,
  postsController.deletePost.bind(postsController)
);

export default router;
