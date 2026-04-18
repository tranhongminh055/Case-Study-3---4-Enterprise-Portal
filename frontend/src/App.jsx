import { useState, useEffect } from 'react';
import EmployeePage from './pages/EmployeePage';
import ReportPage from './pages/ReportPage';
import PayrollPage from './pages/PayrollPage';
import AlertPanel from './components/AlertPanel';

function App() {
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

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1>Enterprise Integration Portal</h1>
          <span className="brand-sub">HR • Payroll • Reporting</span>
        </div>
        <nav>
          <button onClick={() => setActiveTab('employees')} className={activeTab === 'employees' ? 'active' : ''}>
            Employees
          </button>
          <button onClick={() => setActiveTab('reports')} className={activeTab === 'reports' ? 'active' : ''}>
            Reports
          </button>
          <button onClick={() => setActiveTab('payroll')} className={activeTab === 'payroll' ? 'active' : ''}>
            Payroll
          </button>
        </nav>
      </header>

      <main>
        <AlertPanel />
        {activeTab === 'employees' && <EmployeePage />}
        {activeTab === 'reports' && <ReportPage />}
        {activeTab === 'payroll' && <PayrollPage selectedEmployeeId={selectedEmployeeId} />}
      </main>
    </div>
  );
}

export default App;
