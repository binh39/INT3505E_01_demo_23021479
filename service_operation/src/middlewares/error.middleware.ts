import { Request, Response, NextFunction } from 'express';
import { sendError } from '../utils/response.util';

/**
 * Global error handler middleware
 */
export const errorHandler = (
  err: any,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  console.error('Error:', err);

  // Mongoose validation error
  if (err.name === 'ValidationError') {
    const details = Object.values(err.errors).map((e: any) => ({
      field: e.path,
      message: e.message,
    }));

    sendError(res, 'VALIDATION_ERROR', 'Validation failed', 400, details);
    return;
  }

  // Mongoose cast error (invalid ObjectId)
  if (err.name === 'CastError') {
    sendError(res, 'INVALID_ID', `Invalid ${err.path}: ${err.value}`, 400);
    return;
  }

  // Mongoose duplicate key error
  if (err.code === 11000) {
    const field = Object.keys(err.keyPattern)[0];
    sendError(res, 'DUPLICATE_ENTRY', `${field} already exists`, 409);
    return;
  }

  // JWT errors
  if (err.name === 'JsonWebTokenError') {
    sendError(res, 'INVALID_TOKEN', 'Invalid token', 401);
    return;
  }

  if (err.name === 'TokenExpiredError') {
    sendError(res, 'TOKEN_EXPIRED', 'Token has expired', 401);
    return;
  }

  // Default error
  sendError(
    res,
    'INTERNAL_ERROR',
    err.message || 'An unexpected error occurred',
    err.statusCode || 500
  );
};

/**
 * 404 Not Found handler
 */
export const notFoundHandler = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  sendError(res, 'ROUTE_NOT_FOUND', `Route ${req.originalUrl} not found`, 404);
};
