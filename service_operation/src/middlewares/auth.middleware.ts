import { Request, Response, NextFunction } from 'express';
import { AuthRequest } from '../types';
import { extractToken, verifyAccessToken } from '../utils/jwt.util';
import { sendError } from '../utils/response.util';

/**
 * Authentication middleware to verify JWT token
 * Extracts user information from token and adds to request
 */
export const authenticate = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  try {
    const token = extractToken(req.headers.authorization);

    if (!token) {
      sendError(res, 'AUTH_REQUIRED', 'Authentication required', 401);
      return;
    }

    const decoded = verifyAccessToken(token);
    (req as AuthRequest).user = decoded;

    next();
  } catch (error) {
    sendError(res, 'INVALID_TOKEN', 'Invalid or expired token', 401);
  }
};

/**
 * Optional authentication middleware
 * Does not block request if no token is provided
 */
export const optionalAuthenticate = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  try {
    const token = extractToken(req.headers.authorization);

    if (token) {
      const decoded = verifyAccessToken(token);
      (req as AuthRequest).user = decoded;
    }

    next();
  } catch (error) {
    // Invalid token, but continue without authentication
    next();
  }
};
