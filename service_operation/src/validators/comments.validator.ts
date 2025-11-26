import { body, param, query } from 'express-validator';

export const createCommentValidator = [
  param('post_id')
    .notEmpty()
    .withMessage('Post ID is required')
    .isString()
    .withMessage('Post ID must be a string'),
  
  body('content')
    .notEmpty()
    .withMessage('Content is required')
    .isString()
    .withMessage('Content must be a string')
    .isLength({ max: 2000 })
    .withMessage('Content cannot exceed 2000 characters'),
  
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
  
  body('parent_id')
    .optional()
    .isString()
    .withMessage('Parent ID must be a string'),
];

export const updateCommentValidator = [
  param('post_id')
    .notEmpty()
    .withMessage('Post ID is required')
    .isString()
    .withMessage('Post ID must be a string'),
  
  param('comment_id')
    .notEmpty()
    .withMessage('Comment ID is required')
    .isString()
    .withMessage('Comment ID must be a string'),
  
  body('content')
    .optional()
    .isString()
    .withMessage('Content must be a string')
    .isLength({ max: 2000 })
    .withMessage('Content cannot exceed 2000 characters'),
  
  body('media_ids')
    .optional()
    .isArray()
    .withMessage('Media IDs must be an array'),
  
  body('tags')
    .optional()
    .isArray()
    .withMessage('Tags must be an array'),
];

export const commentParamsValidator = [
  param('post_id')
    .notEmpty()
    .withMessage('Post ID is required')
    .isString()
    .withMessage('Post ID must be a string'),
  
  param('comment_id')
    .notEmpty()
    .withMessage('Comment ID is required')
    .isString()
    .withMessage('Comment ID must be a string'),
];

export const getCommentsQueryValidator = [
  param('post_id')
    .notEmpty()
    .withMessage('Post ID is required')
    .isString()
    .withMessage('Post ID must be a string'),
  
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
  
  query('user_id')
    .optional()
    .isString()
    .withMessage('User ID must be a string'),
];
