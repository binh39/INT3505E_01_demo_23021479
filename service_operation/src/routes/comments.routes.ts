import { Router } from 'express';
import commentsController from '../controllers/comments.controller';
import { authenticate, optionalAuthenticate } from '../middlewares/auth.middleware';
import { validate } from '../middlewares/validation.middleware';
import {
  createCommentValidator,
  updateCommentValidator,
  commentParamsValidator,
  getCommentsQueryValidator,
} from '../validators/comments.validator';

const router = Router();

/**
 * GET /posts/:post_id/comments - Get all comments for a post (public)
 */
router.get(
  '/posts/:post_id/comments',
  getCommentsQueryValidator,
  validate,
  optionalAuthenticate,
  commentsController.getComments.bind(commentsController)
);

/**
 * POST /posts/:post_id/comments - Create new comment (authenticated)
 */
router.post(
  '/posts/:post_id/comments',
  createCommentValidator,
  validate,
  authenticate,
  commentsController.createComment.bind(commentsController)
);

/**
 * GET /posts/:post_id/comments/:comment_id - Get single comment (public)
 */
router.get(
  '/posts/:post_id/comments/:comment_id',
  commentParamsValidator,
  validate,
  optionalAuthenticate,
  commentsController.getCommentById.bind(commentsController)
);

/**
 * PATCH /posts/:post_id/comments/:comment_id - Update comment (authenticated)
 */
router.patch(
  '/posts/:post_id/comments/:comment_id',
  updateCommentValidator,
  validate,
  authenticate,
  commentsController.updateComment.bind(commentsController)
);

/**
 * DELETE /posts/:post_id/comments/:comment_id - Delete comment (authenticated)
 */
router.delete(
  '/posts/:post_id/comments/:comment_id',
  commentParamsValidator,
  validate,
  authenticate,
  commentsController.deleteComment.bind(commentsController)
);

export default router;
