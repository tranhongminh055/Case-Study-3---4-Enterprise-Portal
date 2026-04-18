// GENERATE 200 TESTCASES (PASS > FAIL, INTERLEAVED)

const fs = require('fs');
const path = require('path');

const TOTAL = 100; // backend + frontend = 200
const testcases = [];

for (let i = 1; i <= TOTAL; i++) {

  const shouldPass = i % 3 !== 1; // 70% PASS

  // ===== BACKEND =====
  testcases.push({
    id: i,
    type: 'backend',
    description: shouldPass
      ? `Create employee success ${i}`
      : `Create employee fail ${i}`,
    method: 'POST',
    endpoint: '/employees',
    body: shouldPass
      ? {
          first_name: 'Test',
          last_name: 'User',
          email: `test${i}@gmail.com`
        }
      : {
          first_name: '',
          email: 'bad-email'
        },
    expectedStatus: shouldPass ? 201 : 400,
    shouldPass
  });

  // ===== FRONTEND =====
  testcases.push({
    id: i + 1000,
    type: 'frontend',
    description: shouldPass
      ? `UI should show employee ${i}`
      : `UI should NOT show employee ${i}`,
    frontendUrl: 'http://localhost:5174',
    method: 'UI_CHECK',
    email: shouldPass
      ? `test${i}@gmail.com`
      : `notfound${i}@gmail.com`,
    shouldPass
  });
}

// ✅ FIX PATH CHUẨN
const outputPath = path.join(__dirname, 'testcases', 'generated_testcases.json');

// auto create folder nếu thiếu
fs.mkdirSync(path.dirname(outputPath), { recursive: true });

fs.writeFileSync(outputPath, JSON.stringify(testcases, null, 2));

console.log(' Generated 200 testcases at:', outputPath);