import { body, param, query } from 'express-validator';

export const upsertReactionValidator = [
  body('react_type')
    .notEmpty()
    .withMessage('Reaction type is required')
    .isIn(['like', 'love', 'haha', 'wow', 'sad', 'angry'])
    .withMessage('Reaction type must be one of: like, love, haha, wow, sad, angry'),
];

export const postReactionParamsValidator = [
  param('post_id')
    .notEmpty()
    .withMessage('Post ID is required')
    .isString()
    .withMessage('Post ID must be a string'),
];

export const commentReactionParamsValidator = [
  param('comment_id')
    .notEmpty()
    .withMessage('Comment ID is required')
    .isString()
    .withMessage('Comment ID must be a string'),
];

export const getReactionsQueryValidator = [
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
  
  query('react_type')
    .optional()
    .isIn(['like', 'love', 'haha', 'wow', 'sad', 'angry'])
    .withMessage('Reaction type must be one of: like, love, haha, wow, sad, angry'),
];
