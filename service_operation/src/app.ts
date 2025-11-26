import express, { Application } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import morgan from 'morgan';
import config from './config/env';
import { setupSwagger } from './config/swagger';
import routes from './routes';
import { errorHandler, notFoundHandler } from './middlewares/error.middleware';

/**
 * Create and configure Express application
 */
const createApp = (): Application => {
  const app: Application = express();

  // Security middleware
  app.use(helmet());

  // CORS configuration
  app.use(
    cors({
      origin: config.CORS_ORIGIN,
      credentials: true,
    })
  );

  // Compression middleware
  app.use(compression());

  // Request logging
  if (config.NODE_ENV === 'development') {
    app.use(morgan('dev'));
  } else {
    app.use(morgan('combined'));
  }

  // Body parsing middleware
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  // Setup Swagger documentation
  setupSwagger(app);

  // API routes
  app.use(`/${config.API_VERSION}`, routes);

  // Root endpoint
  app.get('/', (req, res) => {
    res.json({
      message: 'Social Media API',
      version: config.API_VERSION,
      documentation: '/api-docs',
    });
  });

  // Error handling
  app.use(notFoundHandler);
  app.use(errorHandler);

  return app;
};

export default createApp;
