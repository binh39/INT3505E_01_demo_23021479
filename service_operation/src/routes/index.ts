import { Router } from 'express';
import postsRoutes from './posts.routes';
import commentsRoutes from './comments.routes';
import reactionsRoutes from './reactions.routes';

const router = Router();

/**
 * Health check endpoint
 */
router.get('/health', (req, res) => {
  res.status(200).json({
    status: 'success',
    message: 'Social Media API is running',
    timestamp: new Date().toISOString(),
  });
});

/**
 * Mount routes
 */
router.use('/posts', postsRoutes);
router.use('/', commentsRoutes); // Comments are under /posts/:post_id/comments
router.use('/', reactionsRoutes); // Reactions are under /posts/:post_id/reactions and /comments/:comment_id/reactions

export default router;
