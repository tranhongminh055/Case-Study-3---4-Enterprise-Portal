import { useEffect, useState } from 'react';
import { getEmployees, getEmployeesWithPayroll, createEmployee, updateEmployee, deleteEmployee } from '../services/api';
import { getAuth } from '../services/auth';
import AuthPanel from '../components/AuthPanel';
import EmployeeForm from '../components/EmployeeForm';
import EmployeeList from '../components/EmployeeList';

function EmployeePage() {
  const auth = getAuth();
  const [employees, setEmployees] = useState([]);
  const [selected, setSelected] = useState(null);
  const [message, setMessage] = useState(null);

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
      <div className="page-grid">
        {!isEmployeeRole && (
          <div className="card">
            <h3>Create / Update Employee</h3>
            <EmployeeForm employee={selected} onSubmit={selected ? handleUpdate : handleCreate} />
          </div>
        )}
        <div className="card" style={isEmployeeRole ? { gridColumn: '1 / -1' } : {}}>
          <h3>Employees</h3>
          {!getAuth().token ? (
            <div>
              <p>Please sign in to view employee data.</p>
              <AuthPanel />
            </div>
          ) : (
            <EmployeeList employees={employees} onEdit={isEmployeeRole ? null : setSelected} onDelete={isEmployeeRole ? null : handleDelete} />
          )}
        </div>
      </div>
    </section>
  );
}

export default EmployeePage;
