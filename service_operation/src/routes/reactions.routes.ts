import { Router } from 'express';
import reactionsController from '../controllers/reactions.controller';
import { authenticate, optionalAuthenticate } from '../middlewares/auth.middleware';
import { validate } from '../middlewares/validation.middleware';
import {
  upsertReactionValidator,
  postReactionParamsValidator,
  commentReactionParamsValidator,
  getReactionsQueryValidator,
} from '../validators/reactions.validator';

const router = Router();

/**
 * POST REACTIONS ROUTES
 */

/**
 * GET /posts/:post_id/reactions - Get all reactions for a post (public)
 */
router.get(
  '/posts/:post_id/reactions',
  postReactionParamsValidator,
  getReactionsQueryValidator,
  validate,
  optionalAuthenticate,
  reactionsController.getPostReactions.bind(reactionsController)
);

/**
 * POST /posts/:post_id/reactions - Upsert reaction for a post (authenticated)
 */
router.post(
  '/posts/:post_id/reactions',
  postReactionParamsValidator,
  upsertReactionValidator,
  validate,
  authenticate,
  reactionsController.upsertPostReaction.bind(reactionsController)
);

/**
 * DELETE /posts/:post_id/reactions - Delete reaction from a post (authenticated)
 */
router.delete(
  '/posts/:post_id/reactions',
  postReactionParamsValidator,
  validate,
  authenticate,
  reactionsController.deletePostReaction.bind(reactionsController)
);

/**
 * COMMENT REACTIONS ROUTES
 */

/**
 * GET /comments/:comment_id/reactions - Get all reactions for a comment (public)
 */
router.get(
  '/comments/:comment_id/reactions',
  commentReactionParamsValidator,
  getReactionsQueryValidator,
  validate,
  optionalAuthenticate,
  reactionsController.getCommentReactions.bind(reactionsController)
);

/**
 * POST /comments/:comment_id/reactions - Upsert reaction for a comment (authenticated)
 */
router.post(
  '/comments/:comment_id/reactions',
  commentReactionParamsValidator,
  upsertReactionValidator,
  validate,
  authenticate,
  reactionsController.upsertCommentReaction.bind(reactionsController)
);

/**
 * DELETE /comments/:comment_id/reactions - Delete reaction from a comment (authenticated)
 */
router.delete(
  '/comments/:comment_id/reactions',
  commentReactionParamsValidator,
  validate,
  authenticate,
  reactionsController.deleteCommentReaction.bind(reactionsController)
);

export default router;
