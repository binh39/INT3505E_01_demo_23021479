import { PaginationQuery, PaginationInfo } from '../types';

/**
 * Parse and validate pagination parameters
 */
export const parsePaginationParams = (query: PaginationQuery): PaginationInfo => {
  const limit = Math.min(Math.max(parseInt(String(query.limit || '20'), 10), 1), 100);
  const offset = Math.max(parseInt(String(query.offset || '0'), 10), 0);

  return {
    limit,
    offset,
    cursor: query.cursor,
  };
};

/**
 * Build pagination metadata
 */
export const buildPaginationMetadata = (
  limit: number,
  offset: number,
  totalItems?: number
): PaginationInfo => {
  const metadata: PaginationInfo = {
    limit,
    offset,
  };

  if (totalItems !== undefined) {
    metadata.total_items = totalItems;
  }

  return metadata;
};

/**
 * Apply pagination to MongoDB query
 */
export const applyPagination = <T>(
  query: any,
  paginationInfo: PaginationInfo
): any => {
  if (paginationInfo.cursor) {
    // Cursor-based pagination
    query = query.where('_id').gt(paginationInfo.cursor);
  } else {
    // Offset-based pagination
    query = query.skip(paginationInfo.offset);
  }

  return query.limit(paginationInfo.limit);
};

/**
 * Apply sorting to MongoDB query
 */
export const applySorting = (
  query: any,
  sortBy: string = 'created_at',
  order: 'asc' | 'desc' = 'desc'
): any => {
  const sortDirection = order === 'asc' ? 1 : -1;
  return query.sort({ [sortBy]: sortDirection });
};
