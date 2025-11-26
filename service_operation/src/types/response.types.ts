import { Request } from 'express';

// Extend Express Request to include user info from JWT
export interface AuthRequest extends Request {
  user?: {
    id: string;
    email?: string;
  };
}

// HATEOAS Links
export interface Link {
  href: string;
  method: string;
}

export interface Links {
  [key: string]: Link;
}

// Pagination
export interface PaginationInfo {
  limit: number;
  offset: number;
  total_items?: number;
  cursor?: string;
}

export interface Metadata {
  pagination?: PaginationInfo;
}

// Base Response Structure
export interface SuccessResponse<T> {
  status: 'success';
  message?: string;
  data: T;
  _links?: Links;
  metadata?: Metadata;
}

export interface ErrorDetail {
  field?: string;
  message: string;
}

export interface ErrorResponse {
  status: 'error';
  code: string;
  message: string;
  details?: ErrorDetail[];
}

// Query Parameters
export interface PaginationQuery {
  limit?: number;
  offset?: number;
  cursor?: string;
}

export interface SortQuery {
  sort_by?: string;
  order?: 'asc' | 'desc';
}

export interface PostQueryParams extends PaginationQuery, SortQuery {
  q?: string;
  user_id?: string;
  status?: string;
  tag?: string[];
}

export interface ReactionQueryParams extends PaginationQuery {
  react_type?: 'like' | 'love' | 'haha' | 'wow' | 'sad' | 'angry';
}

export interface CommentQueryParams extends PaginationQuery {
  user_id?: string;
}
