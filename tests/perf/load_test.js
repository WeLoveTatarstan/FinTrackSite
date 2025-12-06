import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 5 },
    { duration: '20s', target: 15 },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<600'],
    http_req_failed: ['rate<0.01'],
  },
  maxDuration: '60s', // Maximum test duration
  teardownTimeout: '10s', // Timeout for teardown
};

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8000';

export default function () {
  const params = {
    timeout: '10s', // Request timeout
  };
  const res = http.get(`${BASE_URL}/health/`, params);
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response includes ok': (r) => {
      try {
        return r.json('status') === 'ok';
      } catch (e) {
        return false;
      }
    },
  });
  sleep(1);
}
