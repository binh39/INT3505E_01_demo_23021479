import { Post } from '../models/post.model';
import { Reaction } from '../models/reaction.model';
import { Comment } from '../models/comment.model';
import {
  IPost,
  PostCreateInput,
  PostUpdateInput,
  PostResponse,
  PostQueryParams,
} from '../types';
import { parsePaginationParams, applySorting, applyPagination } from '../utils/pagination.util';

/**
 * Posts Service - Business logic for posts
 */
class PostsService {
  /**
   * Get all posts with filtering, pagination, and sorting
   */
  async getPosts(queryParams: PostQueryParams): Promise<{ posts: PostResponse[]; total?: number }> {
    const paginationInfo = parsePaginationParams(queryParams);
    const { q, user_id, status, tag, sort_by = 'created_at', order = 'desc' } = queryParams;

    // Build filter query
    const filter: any = {};

    if (user_id) {
      filter.user_id = user_id;
    }

    if (status !== undefined) {
      filter.is_moderated = status === 'true';
    }

    if (tag && Array.isArray(tag)) {
      filter.tags = { $in: tag };
    }

    if (q) {
      filter.$text = { $search: q };
    }

    // Build query
    let query = Post.find(filter);

    // Apply sorting
    query = applySorting(query, sort_by, order);

    // Apply pagination
    query = applyPagination(query, paginationInfo);

    // Execute query
    const posts = await query.lean().exec();

    // Get total count for pagination metadata (only for offset-based)
    let total: number | undefined;
    if (!paginationInfo.cursor) {
      total = await Post.countDocuments(filter);
    }

    return {
      posts: posts.map(this.formatPostResponse),
      total,
    };
  }

  /**
   * Get a single post by ID
   */
  async getPostById(postId: string): Promise<PostResponse | null> {
    const post = await Post.findById(postId).lean().exec();
    return post ? this.formatPostResponse(post) : null;
  }

  /**
   * Create a new post
   */
  async createPost(userId: string, data: PostCreateInput): Promise<PostResponse> {
    const post = await Post.create({
      ...data,
      user_id: userId,
    });

    return this.formatPostResponse(post.toObject());
  }

  /**
   * Update a post
   */
  async updatePost(
    postId: string,
    userId: string,
    data: PostUpdateInput
  ): Promise<PostResponse | null> {
    const post = await Post.findOneAndUpdate(
      { _id: postId, user_id: userId },
      { $set: data },
      { new: true, runValidators: true }
    ).lean().exec();

    return post ? this.formatPostResponse(post) : null;
  }

  /**
   * Delete a post
   */
  async deletePost(postId: string, userId: string): Promise<boolean> {
    const result = await Post.deleteOne({ _id: postId, user_id: userId });

    if (result.deletedCount > 0) {
      // Clean up associated reactions and comments
      await Promise.all([
        Reaction.deleteMany({ target_id: postId, target_type: 'post' }),
        Comment.deleteMany({ post_id: postId }),
      ]);
      return true;
    }

    return false;
  }

  /**
   * Check if post exists
   */
  async postExists(postId: string): Promise<boolean> {
    const count = await Post.countDocuments({ _id: postId });
    return count > 0;
  }

  /**
   * Increment reaction count
   */
  async incrementReactionCount(postId: string): Promise<void> {
    await Post.findByIdAndUpdate(postId, { $inc: { likes_count: 1 } });
  }

  /**
   * Decrement reaction count
   */
  async decrementReactionCount(postId: string): Promise<void> {
    await Post.findByIdAndUpdate(postId, { $inc: { likes_count: -1 } });
  }

  /**
   * Increment comment count
   */
  async incrementCommentCount(postId: string): Promise<void> {
    await Post.findByIdAndUpdate(postId, { $inc: { comments_count: 1 } });
  }

  /**
   * Decrement comment count
   */
  async decrementCommentCount(postId: string): Promise<void> {
    await Post.findByIdAndUpdate(postId, { $inc: { comments_count: -1 } });
  }

  /**
   * Format post for response
   */
  private formatPostResponse(post: any): PostResponse {
    return {
      id: post._id.toString(),
      user_id: post.user_id,
      content: post.content,
      media_ids: post.media_ids,
      tags: post.tags,
      post_share_id: post.post_share_id,
      group_id: post.group_id,
      visibility: post.visibility,
      likes_count: post.likes_count,
      comments_count: post.comments_count,
      shares_count: post.shares_count,
      is_moderated: post.is_moderated,
      created_at: post.created_at?.toISOString() || new Date().toISOString(),
      updated_at: post.updated_at?.toISOString() || new Date().toISOString(),
    };
  }
}

export default new PostsService();
