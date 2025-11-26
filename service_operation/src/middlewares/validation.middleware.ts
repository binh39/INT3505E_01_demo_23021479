import { Request, Response, NextFunction } from 'express';
import { validationResult } from 'express-validator';
import { sendError } from '../utils/response.util';

/**
 * Validation middleware to check express-validator results
 */
export const validate = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const errors = validationResult(req);

  if (!errors.isEmpty()) {
    const details = errors.array().map((error: any) => ({
      field: error.path || error.param,
      message: error.msg,
    }));

    sendError(res, 'INVALID_INPUT', 'Validation failed', 400, details);
    return;
  }

  next();
};
