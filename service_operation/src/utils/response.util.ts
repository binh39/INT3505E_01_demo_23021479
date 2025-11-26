import { Response } from 'express';
import config from '../config/env';
import { SuccessResponse, ErrorResponse, Links, Metadata } from '../types';

const API_BASE_URL = `http://localhost:${config.PORT}/${config.API_VERSION}`;

/**
 * Send a successful response with HATEOAS links
 */
export const sendSuccess = <T>(
  res: Response,
  data: T,
  statusCode: number = 200,
  message?: string,
  links?: Links,
  metadata?: Metadata
): Response => {
  const response: SuccessResponse<T> = {
    status: 'success',
    data,
  };

  if (message) response.message = message;
  if (links) response._links = links;
  if (metadata) response.metadata = metadata;

  return res.status(statusCode).json(response);
};

/**
 * Send an error response
 */
export const sendError = (
  res: Response,
  code: string,
  message: string,
  statusCode: number = 400,
  details?: Array<{ field?: string; message: string }>
): Response => {
  const response: ErrorResponse = {
    status: 'error',
    code,
    message,
  };

  if (details) response.details = details;

  return res.status(statusCode).json(response);
};

/**
 * Generate HATEOAS links for a post
 */
export const generatePostLinks = (postId: string): Links => {
  return {
    self: {
      href: `${API_BASE_URL}/posts/${postId}`,
      method: 'GET',
    },
    update: {
      href: `${API_BASE_URL}/posts/${postId}`,
      method: 'PATCH',
    },
    delete: {
      href: `${API_BASE_URL}/posts/${postId}`,
      method: 'DELETE',
    },
    reactions: {
      href: `${API_BASE_URL}/posts/${postId}/reactions`,
      method: 'GET',
    },
    add_reaction: {
      href: `${API_BASE_URL}/posts/${postId}/reactions`,
      method: 'POST',
    },
    comments: {
      href: `${API_BASE_URL}/posts/${postId}/comments`,
      method: 'GET',
    },
    add_comment: {
      href: `${API_BASE_URL}/posts/${postId}/comments`,
      method: 'POST',
    },
  };
};

/**
 * Generate HATEOAS links for a comment
 */
export const generateCommentLinks = (postId: string, commentId: string): Links => {
  return {
    self: {
      href: `${API_BASE_URL}/posts/${postId}/comments/${commentId}`,
      method: 'GET',
    },
    update: {
      href: `${API_BASE_URL}/posts/${postId}/comments/${commentId}`,
      method: 'PATCH',
    },
    delete: {
      href: `${API_BASE_URL}/posts/${postId}/comments/${commentId}`,
      method: 'DELETE',
    },
    reactions: {
      href: `${API_BASE_URL}/comments/${commentId}/reactions`,
      method: 'GET',
    },
    add_reaction: {
      href: `${API_BASE_URL}/comments/${commentId}/reactions`,
      method: 'POST',
    },
    post: {
      href: `${API_BASE_URL}/posts/${postId}`,
      method: 'GET',
    },
  };
};

/**
 * Generate HATEOAS links for posts collection
 */
export const generatePostsCollectionLinks = (query: Record<string, any> = {}): Links => {
  const queryString = new URLSearchParams(query).toString();
  const baseUrl = `${API_BASE_URL}/posts`;

  return {
    self: {
      href: queryString ? `${baseUrl}?${queryString}` : baseUrl,
      method: 'GET',
    },
    create: {
      href: baseUrl,
      method: 'POST',
    },
  };
};

/**
 * Generate HATEOAS links for comments collection
 */
export const generateCommentsCollectionLinks = (postId: string, query: Record<string, any> = {}): Links => {
  const queryString = new URLSearchParams(query).toString();
  const baseUrl = `${API_BASE_URL}/posts/${postId}/comments`;

  return {
    self: {
      href: queryString ? `${baseUrl}?${queryString}` : baseUrl,
      method: 'GET',
    },
    create: {
      href: baseUrl,
      method: 'POST',
    },
    post: {
      href: `${API_BASE_URL}/posts/${postId}`,
      method: 'GET',
    },
  };
};

/**
 * Generate HATEOAS links for reactions collection
 */
export const generateReactionsCollectionLinks = (targetId: string, targetType: 'posts' | 'comments'): Links => {
  const baseUrl = `${API_BASE_URL}/${targetType}/${targetId}/reactions`;

  return {
    self: {
      href: baseUrl,
      method: 'GET',
    },
    upsert: {
      href: baseUrl,
      method: 'POST',
    },
    delete: {
      href: baseUrl,
      method: 'DELETE',
    },
  };
};
