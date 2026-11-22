
const app = require('./app');
const { Eureka } = require('eureka-js-client');

const PORT = Number(process.env.PORT || 8083);

const eureka = new Eureka({
  instance: {
    app: 'MEETING',
    instanceId: `localhost:meeting:${PORT}`,
    hostName: 'localhost',
    ipAddr: '127.0.0.1',

    port: {
      '$': PORT,
      '@enabled': 'true'
    },

    vipAddress: 'meeting',
    statusPageUrl: `http://localhost:${PORT}/health`,
    healthCheckUrl: `http://localhost:${PORT}/health`,
    homePageUrl: `http://localhost:${PORT}/`,

    dataCenterInfo: {
      '@class':
          'com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo',
      name: 'MyOwn'
    }
  },

  eureka: {
    host: 'localhost',
    port: 8761,
    servicePath: '/eureka/apps/',
    registerWithEureka: true,
    fetchRegistry: true
  }
});

const server = app.listen(PORT, () => {
  console.log(
      `Meeting microservice running on http://localhost:${PORT}`
  );
  console.log(
      `Swagger UI: http://localhost:${PORT}/swagger-ui`
  );

  // Register the service after Express starts
  eureka.start(error => {
    if (error) {
      console.error('Eureka registration failed:', error);
    } else {
      console.log('MEETING registered with Eureka');
    }
  });
});

// Stop heartbeats and deregister on shutdown
function shutdown() {
  eureka.stop(() => {
    server.close(() => {
      process.exit(0);
    });
  });
}

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
