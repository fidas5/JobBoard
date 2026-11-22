
const express = require('express');
const swaggerUi = require('swagger-ui-express');
const openapiSpec = require('./config/swagger');
const meetingRoutes = require('./routes/meeting.routes');

const app = express();

app.use(express.json());

// ========================================
// METRICS MIDDLEWARE
// ========================================

let totalRequests = 0;

app.use((req, res, next) => {
  totalRequests++;
  next();
});

// ========================================
// ACTUATOR - HEALTH
// ========================================

app.get('/actuator/health', (req, res) => {
  res.status(200).json({
    status: 'UP',
    components: {
      meeting: {
        status: 'UP'
      }
    }
  });
});

// ========================================
// ACTUATOR - INFO
// ========================================

app.get('/actuator/info', (req, res) => {
  res.status(200).json({
    app: {
      name: 'meeting',
      version: '1.0.0',
      description: 'JobBoard Meeting Microservice',
      technology: 'Node.js / Express'
    }
  });
});

// ========================================
// ACTUATOR - METRICS
// ========================================

app.get('/actuator/metrics', (req, res) => {
  const memory = process.memoryUsage();
  const cpu = process.cpuUsage();

  res.status(200).json({
    service: 'meeting',
    uptime_seconds: Math.round(process.uptime()),
    memory: {
      rss_bytes: memory.rss,
      heap_used_bytes: memory.heapUsed,
      heap_total_bytes: memory.heapTotal
    },
    cpu: {
      user_microseconds: cpu.user,
      system_microseconds: cpu.system
    },
    http: {
      total_requests: totalRequests
    }
  });
});

// ========================================
// HEALTH CHECK FOR EUREKA
// ========================================

app.get('/health', (req, res) => {
  res.status(200).json({
    service: 'meeting',
    status: 'UP'
  });
});

// ========================================
// SWAGGER DOCUMENTATION
// ========================================

app.get('/v3/api-docs', (req, res) => {
  res.json(openapiSpec);
});

app.use(
    '/swagger-ui',
    swaggerUi.serve,
    swaggerUi.setup(openapiSpec)
);

// ========================================
// MEETING API ROUTES
// ========================================

app.use('/api/meetings', meetingRoutes);

// ========================================
// 404 - UNKNOWN ROUTES
// ========================================

app.use((req, res) => {
  res.status(404).json({
    status: 404,
    error: 'Not Found',
    message: `Route ${req.method} ${req.originalUrl} not found`
  });
});

// ========================================
// GLOBAL ERROR HANDLER
// ========================================

app.use((err, req, res, next) => {
  const status = err.status || 500;

  res.status(status).json({
    status,
    error: status === 500
        ? 'Internal Server Error'
        : 'Error',
    message: err.message
  });
});

module.exports = app;
