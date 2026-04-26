import { useEffect, useState } from 'react';
import { getEmployees, getEmployeesWithPayroll, createEmployee, updateEmployee, deleteEmployee } from '../services/api';
import { getAuth } from '../services/auth';
import AuthPanel from '../components/AuthPanel';
import EmployeeForm from '../components/EmployeeForm';
import EmployeeList from '../components/EmployeeList';
import EmployeeDashboard from '../components/EmployeeDashboard';

function EmployeePage({ activeTab = 'employees' }) {
  const auth = getAuth();
  const [employees, setEmployees] = useState([]);
  const [selected, setSelected] = useState(null);
  const [message, setMessage] = useState(null);
  const activeOperation = activeTab === 'create-employee' ? 'create'
    : activeTab === 'edit-employee' ? 'edit'
    : activeTab === 'delete-employee' ? 'delete'
    : activeTab === 'view-employees' ? 'view'
    : null;

  const loadEmployees = async () => {
    try {
      const auth = getAuth();
      // Admins see combined employee+payroll data, others see basic employee list
      const response = auth && auth.role === 'Admin' ? await getEmployeesWithPayroll() : await getEmployees();
      setEmployees(response.data || []);
    } catch (error) {
      setMessage(error?.response?.data?.message || 'Unable to load employees. Please login to view data.');
    }
  };

  useEffect(() => {
    const auth = getAuth();
    if (!auth || !auth.token) {
      setMessage('Please login to view employees.');
      return;
    }
    loadEmployees();

    function onAuth() {
      const a = getAuth();
      if (a && a.token) {
        setMessage(null);
        loadEmployees();
      } else {
        setEmployees([]);
        setMessage('Please login to view employees.');
      }
    }
    window.addEventListener('authChanged', onAuth);
    return () => window.removeEventListener('authChanged', onAuth);
  }, []);

  const handleCreate = async (record) => {
    // client-side uniqueness check to avoid unnecessary API calls
    if (record.email) {
      const exists = employees.some((e) => e.email && e.email.toLowerCase() === record.email.toLowerCase());
      if (exists) {
        setMessage('Email already used by another employee');
        return;
      }
    }
    try {
      await createEmployee(record);
      await loadEmployees();
      setSelected(null);
      setMessage('Employee created successfully.');
    } catch (error) {
      setMessage(error?.response?.data?.message || 'Create failed.');
    }
  };

  const handleUpdate = async (id, record) => {
    // client-side uniqueness check (exclude current record)
    if (record.email) {
      const exists = employees.some((e) => e.email && e.email.toLowerCase() === record.email.toLowerCase() && e.id !== id);
      if (exists) {
        setMessage('Email already used by another employee');
        return;
      }
    }
    try {
      await updateEmployee(id, record);
      await loadEmployees();
      setSelected(null);
      setMessage('Employee updated successfully.');
    } catch (error) {
      setMessage(error?.response?.data?.message || 'Update failed.');
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteEmployee(id);
      await loadEmployees();
      setSelected(null);
      setMessage('Employee deleted successfully.');
    } catch (error) {
      setMessage(error?.response?.data?.message || 'Delete failed. Employee may have existing salary/dividend links.');
    }
  };

  // Role-based access: Employee role can only view
  const isEmployeeRole = auth?.role === 'Employee';

  return (
    <section className="page-section">
      <h2>Employee Management</h2>
      {message && <div className="flash-message">{message}</div>}
      <div className={isEmployeeRole ? 'page-grid' : 'page-grid employee-grid'}>
        {!isEmployeeRole && (
          <aside className="card side-panel">
            <div className="panel-header">
              <h3>Employee Operations</h3>
              <p className="muted">Quick access to employee management features.</p>
            </div>

            <div className="panel-actions">
              <button type="button" onClick={() => window.dispatchEvent(new CustomEvent('navigate', { detail: { tab: 'view-employees' } }))}>
                View employees
              </button>
              <button type="button" onClick={() => window.dispatchEvent(new CustomEvent('navigate', { detail: { tab: 'create-employee' } }))}>
                Create employee
              </button>
              <button type="button" onClick={() => window.dispatchEvent(new CustomEvent('navigate', { detail: { tab: 'edit-employee' } }))}>
                Edit employee
              </button>
              <button type="button" onClick={() => window.dispatchEvent(new CustomEvent('navigate', { detail: { tab: 'delete-employee' } }))}>
                Delete employee
              </button>
              <button type="button" onClick={() => window.dispatchEvent(new CustomEvent('navigate', { detail: { tab: 'payroll' } }))}>
                Payroll
              </button>
              <button type="button" onClick={() => window.dispatchEvent(new CustomEvent('navigate', { detail: { tab: 'reports' } }))}>
                Reports
              </button>
            </div>
          </aside>
        )}
        <div className="card employees-card" style={isEmployeeRole ? { gridColumn: '1 / -1' } : {}}>
          <div className="list-header">
            <h3>{activeOperation === 'view' ? 'View employees' : activeOperation === 'create' ? 'Create employee' : activeOperation === 'edit' ? 'Edit employee' : activeOperation === 'delete' ? 'Delete employee' : 'Employees'}</h3>
            {!isEmployeeRole && selected && (
              <button type="button" className="secondary" onClick={() => setSelected(null)}>
                Clear selection
              </button>
            )}
          </div>
          {!getAuth().token ? (
            <div>
              <p>Please sign in to view employee data.</p>
              <AuthPanel />
            </div>
          ) : activeOperation === 'view' ? (
            <EmployeeList employees={employees} onEdit={null} onDelete={null} />
          ) : activeOperation === 'create' ? (
            <EmployeeForm employee={null} onSubmit={handleCreate} />
          ) : activeOperation === 'edit' ? (
            selected ? (
              <EmployeeForm employee={selected} onSubmit={handleUpdate} />
            ) : (
              <>
                <p className="muted">Select an employee from the table below to edit.</p>
                <EmployeeList employees={employees} onEdit={setSelected} onDelete={null} />
              </>
            )
          ) : activeOperation === 'delete' ? (
            selected ? (
              <>
                <p className="muted">Delete employee {selected.email || selected.id}?</p>
                <button type="button" className="secondary danger" onClick={() => {
                  handleDelete(selected.id);
                  setSelected(null);
                }}>
                  Confirm Delete
                </button>
              </>
            ) : (
              <>
                <p className="muted">Select an employee from the table below to delete.</p>
                <EmployeeList employees={employees} onEdit={null} onDelete={(id) => {
                  const employee = employees.find((emp) => emp.id === id);
                  setSelected(employee || null);
                }} />
              </>
            )
          ) : (
            <EmployeeDashboard employees={employees} />
          )}
        </div>
      </div>
    </section>
  );
}

export default EmployeePage;
