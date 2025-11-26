import createApp from './app';
import config from './config/env';
import database from './config/database';

/**
 * Start the server
 */
const startServer = async (): Promise<void> => {
  try {
    // Connect to database
    await database.connect();

    // Create Express app
    const app = createApp();

    // Start listening
    const server = app.listen(config.PORT, () => {
      console.log(`
╔════════════════════════════════════════════════════════╗
║                                                        ║
║        🚀 Social Media API Server Started             ║
║                                                        ║
║        Environment: ${config.NODE_ENV.padEnd(36)}║
║        Port:        ${config.PORT.toString().padEnd(36)}║
║        API Version: ${config.API_VERSION.padEnd(36)}║
║                                                        ║
║        API Docs:    http://localhost:${config.PORT}/api-docs     ║
║        Health:      http://localhost:${config.PORT}/${config.API_VERSION}/health  ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
      `);
    });

    // Graceful shutdown
    const gracefulShutdown = async (signal: string) => {
      console.log(`\n${signal} received. Starting graceful shutdown...`);

      server.close(async () => {
        console.log('HTTP server closed');

        try {
          await database.disconnect();
          console.log('Database connection closed');
          process.exit(0);
        } catch (error) {
          console.error('Error during shutdown:', error);
          process.exit(1);
        }
      });

      // Force shutdown after 30 seconds
      setTimeout(() => {
        console.error('Forcing shutdown after timeout');
        process.exit(1);
      }, 30000);
    };

    // Listen for termination signals
    process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
    process.on('SIGINT', () => gracefulShutdown('SIGINT'));

    // Handle uncaught exceptions
    process.on('uncaughtException', (error) => {
      console.error('Uncaught Exception:', error);
      gracefulShutdown('uncaughtException');
    });

    // Handle unhandled promise rejections
    process.on('unhandledRejection', (reason, promise) => {
      console.error('Unhandled Rejection at:', promise, 'reason:', reason);
      gracefulShutdown('unhandledRejection');
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
};

// Start the server
startServer();
