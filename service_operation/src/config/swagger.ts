import { Express } from 'express';
import swaggerUi from 'swagger-ui-express';
import YAML from 'yamljs';
import path from 'path';

export const setupSwagger = (app: Express): void => {
  try {
    // Load OpenAPI specification
    const swaggerDocument = YAML.load(
      path.join(__dirname, '../../../openapi/openapi.yaml')
    );

    // Swagger UI options
    const options = {
      explorer: true,
      customCss: '.swagger-ui .topbar { display: none }',
      customSiteTitle: 'Social Media API Documentation',
    };

    // Setup Swagger UI
    app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument, options));

    console.log('📚 Swagger documentation available at /api-docs');
  } catch (error) {
    console.error('❌ Failed to load Swagger documentation:', error);
  }
};
