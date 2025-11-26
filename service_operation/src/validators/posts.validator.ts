import { body, param, query } from 'express-validator';

export const createPostValidator = [
  body('content')
    .notEmpty()
    .withMessage('Content is required')
    .isString()
    .withMessage('Content must be a string')
    .isLength({ max: 10000 })
    .withMessage('Content cannot exceed 10000 characters'),
  
  body('media_ids')
    .optional()
    .isArray()
    .withMessage('Media IDs must be an array'),
  
  body('media_ids.*')
    .optional()
    .isString()
    .withMessage('Each media ID must be a string'),
  
  body('tags')
    .optional()
    .isArray()
    .withMessage('Tags must be an array'),
  
  body('tags.*')
    .optional()
    .isString()
    .withMessage('Each tag must be a string'),
  
  body('post_share_id')
    .optional()
    .isString()
    .withMessage('Post share ID must be a string'),
  
  body('group_id')
    .optional()
    .isString()
    .withMessage('Group ID must be a string'),
  
  body('visibility')
    .optional()
    .isIn(['public', 'friends', 'private'])
    .withMessage('Visibility must be one of: public, friends, private'),
];

export const updatePostValidator = [
  param('post_id')
    .notEmpty()
    .withMessage('Post ID is required')
    .isString()
    .withMessage('Post ID must be a string'),
  
  body('content')
    .optional()
    .isString()
    .withMessage('Content must be a string')
    .isLength({ max: 10000 })
    .withMessage('Content cannot exceed 10000 characters'),
  
  body('media_ids')
    .optional()
    .isArray()
    .withMessage('Media IDs must be an array'),
  
  body('tags')
    .optional()
    .isArray()
    .withMessage('Tags must be an array'),
  
  body('visibility')
    .optional()
    .isIn(['public', 'friends', 'private'])
    .withMessage('Visibility must be one of: public, friends, private'),
];

export const postIdValidator = [
  param('post_id')
    .notEmpty()
    .withMessage('Post ID is required')
    .isString()
    .withMessage('Post ID must be a string'),
];

export const getPostsQueryValidator = [
  query('limit')
    .optional()
    .isInt({ min: 1, max: 100 })
    .withMessage('Limit must be between 1 and 100'),
  
  query('offset')
    .optional()
    .isInt({ min: 0 })
    .withMessage('Offset must be a non-negative integer'),
  
  query('cursor')
    .optional()
    .isString()
    .withMessage('Cursor must be a string'),
  
  query('q')
    .optional()
    .isString()
    .withMessage('Search query must be a string'),
  
  query('user_id')
    .optional()
    .isString()
    .withMessage('User ID must be a string'),
  
  query('status')
    .optional()
    .isIn(['true', 'false'])
    .withMessage('Status must be true or false'),
  
  query('sort_by')
    .optional()
    .isString()
    .withMessage('Sort by must be a string'),
  
  query('order')
    .optional()
    .isIn(['asc', 'desc'])
    .withMessage('Order must be asc or desc'),
];
