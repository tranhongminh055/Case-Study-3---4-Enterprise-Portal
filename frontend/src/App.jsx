import { useState, useEffect } from 'react';
import EmployeePage from './pages/EmployeePage';
import ReportPage from './pages/ReportPage';
import PayrollPage from './pages/PayrollPage';
import AlertPanel from './components/AlertPanel';
import AuthPanel from './components/AuthPanel';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import { getAuth, logout } from './services/auth';

function Dashboard({ onLogout }) {
  const auth = getAuth();
  const [activeTab, setActiveTab] = useState('employees');
  const [selectedEmployeeId, setSelectedEmployeeId] = useState(null);

  // allow other components to request navigation via CustomEvent
  useEffect(() => {
    function onNavigate(e) {
      const { tab, employeeId } = e.detail || {};
      if (tab) setActiveTab(tab);
      if (typeof employeeId !== 'undefined') setSelectedEmployeeId(employeeId);
    }
    window.addEventListener('navigate', onNavigate);
    return () => window.removeEventListener('navigate', onNavigate);
  }, []);

  // Role-based access: Employee role can only access Employees tab
  const isEmployeeRole = auth?.role === 'Employee';

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1>Enterprise Integration Portal</h1>
          <span className="brand-sub">HR • Payroll • Reporting</span>
        </div>
        <nav>
          <button onClick={() => setActiveTab('employees')} className={activeTab.startsWith('employees') || activeTab.startsWith('create-employee') || activeTab.startsWith('edit-employee') || activeTab.startsWith('delete-employee') || activeTab === 'view-employees' ? 'active' : ''}>
            Employees
          </button>
          {!isEmployeeRole && (
            <>
              <button onClick={() => setActiveTab('reports')} className={activeTab === 'reports' ? 'active' : ''}>
                Reports
              </button>
              <button onClick={() => setActiveTab('payroll')} className={activeTab === 'payroll' ? 'active' : ''}>
                Payroll
              </button>
            </>
          )}
        </nav>
        <AuthPanel />
      </header>

      <main>
        <AlertPanel />
        {(activeTab === 'employees' || activeTab === 'create-employee' || activeTab === 'edit-employee' || activeTab === 'delete-employee' || activeTab === 'view-employees') && (
          <EmployeePage activeTab={activeTab} />
        )}
        {activeTab === 'reports' && !isEmployeeRole && <ReportPage />}
        {activeTab === 'payroll' && !isEmployeeRole && <PayrollPage selectedEmployeeId={selectedEmployeeId} />}
      </main>
    </div>
  );
}

function AuthScreen() {
  const [mode, setMode] = useState('login'); // 'login' hoặc 'register'
  const [auth, setAuth] = useState(getAuth());

  useEffect(() => {
    function onAuth(e) {
      setAuth(getAuth());
    }
    window.addEventListener('authChanged', onAuth);
    return () => window.removeEventListener('authChanged', onAuth);
  }, []);

  const handleLoginSuccess = () => {
    setAuth(getAuth());
  };

  const handleRegisterSuccess = () => {
    setMode('login');
  };

  return (
    <div className="auth-screen">
      <div className="auth-container">
        <div className="auth-header">
          <h1>Enterprise Integration Portal</h1>
          <span className="brand-sub">HR • Payroll • Reporting</span>
        </div>

        <div className="auth-content">
          {mode === 'login' ? (
            <LoginForm 
              onSuccess={handleLoginSuccess}
              onCancel={() => setMode('register')}
            />
          ) : (
            <RegisterForm 
              onSuccess={handleRegisterSuccess}
              onCancel={() => setMode('login')}
            />
          )}

          <div className="auth-toggle">
            {mode === 'login' ? (
              <p>
                Chưa có tài khoản?{' '}
                <button type="button" onClick={() => setMode('register')} className="link-button">
                  Đăng ký ngay
                </button>
              </p>
            ) : (
              <p>
                Đã có tài khoản?{' '}
                <button type="button" onClick={() => setMode('login')} className="link-button">
                  Đăng nhập
                </button>
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [auth, setAuth] = useState(getAuth());

  useEffect(() => {
    function onAuth(e) {
      setAuth(getAuth());
    }
    window.addEventListener('authChanged', onAuth);
    return () => window.removeEventListener('authChanged', onAuth);
  }, []);

  // Hiển thị màn login/đăng ký nếu chưa đăng nhập
  if (!auth?.token) {
    return <AuthScreen />;
  }

  // Hiển thị dashboard nếu đã đăng nhập
  return <Dashboard onLogout={() => setAuth(getAuth())} />;
}

export default App;
