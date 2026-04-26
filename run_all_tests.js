// run_all_tests.js - Script to run all tests automatically
const { execSync, spawn } = require('child_process');
const path = require('path');

console.log('🚀 Starting Comprehensive Test Suite...\n');

// Function to run command and handle errors
function runCommand(command, cwd, description) {
  try {
    console.log(`📋 ${description}...`);
    execSync(command, { cwd, stdio: 'inherit' });
    console.log(`✅ ${description} completed\n`);
    return true;
  } catch (error) {
    console.log(`❌ ${description} failed:`, error.message);
    return false;
  }
}

// Check if backend dependencies are installed
console.log('🔍 Checking backend dependencies...');
if (!runCommand('python -c "import fastapi, uvicorn, sqlalchemy"', path.join(__dirname, 'backend'), 'Backend dependencies check')) {
  console.log('Please install backend dependencies: pip install -r backend/requirements.txt');
  process.exit(1);
}

// Check if frontend dependencies are installed
console.log('🔍 Checking frontend dependencies...');
if (!runCommand('npm list cypress', path.join(__dirname, 'frontend'), 'Frontend dependencies check')) {
  console.log('Please install frontend dependencies: cd frontend && npm install');
  process.exit(1);
}

// Generate latest test file
console.log('🔧 Generating test files...');
runCommand('node frontend/cypress/test-suite/generate_test.js', __dirname, 'Generate Cypress tests');

// Start backend server
console.log('🖥️  Starting backend server...');
const backendProcess = spawn('uvicorn', ['main:app', '--reload', '--host', '0.0.0.0', '--port', '8000'], {
  cwd: path.join(__dirname, 'backend'),
  stdio: 'inherit',
  detached: true
});

// Wait for backend to start
console.log('⏳ Waiting for backend to start...');
setTimeout(() => {
  // Start frontend server
  console.log('🌐 Starting frontend server...');
  const frontendProcess = spawn('npm', ['run', 'dev'], {
    cwd: path.join(__dirname, 'frontend'),
    stdio: 'inherit',
    detached: true
  });

  // Wait for frontend to start
  console.log('⏳ Waiting for frontend to start...');
  setTimeout(() => {
    // Run Cypress tests
    console.log('🧪 Running Cypress tests...');
    try {
      execSync('npx cypress run --spec "cypress/e2e/comprehensive_test.cy.js" --headless', {
        cwd: path.join(__dirname, 'frontend'),
        stdio: 'inherit'
      });
      console.log('✅ All tests completed successfully!');
    } catch (error) {
      console.log('❌ Tests failed:', error.message);
      process.exit(1);
    } finally {
      // Cleanup processes
      console.log('🧹 Cleaning up...');
      try {
        process.kill(-backendProcess.pid);
        process.kill(-frontendProcess.pid);
      } catch (e) {
        // Ignore cleanup errors
      }
    }
  }, 10000); // Wait 10 seconds for frontend
}, 5000); // Wait 5 seconds for backend