function EmployeeList({ employees, onEdit, onDelete }) {
  const employeeRows = employees.map((employee) => {
    const name = employee.full_name
      ? employee.full_name
      : `${employee.first_name || ''} ${employee.last_name || ''}`.trim();

    return (
      <tr key={employee.id}>
        <td>{employee.id}</td>
        <td className="name-cell">{name || 'N/A'}</td>
        <td>{employee.email}</td>
        <td>{employee.latest_salary && employee.latest_salary.amount ? employee.latest_salary.amount : 'N/A'}</td>
        <td>{employee.status}</td>
        <td>{employee.department_id || 'N/A'}</td>
        <td>{employee.position_id || 'N/A'}</td>
        <td>
          {onEdit && (
            <button className="small" onClick={() => onEdit(employee)}>
              Edit
            </button>
          )}
          {onDelete && (
            <button className="small secondary" onClick={() => onDelete(employee.id)}>
              Delete
            </button>
          )}
          {!onEdit && !onDelete && <span className="muted">Read-only</span>}
        </td>
      </tr>
    );
  });

  return (
    <div className="entity-table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Salary</th>
            <th>Status</th>
            <th>Department</th>
            <th>Position</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {employeeRows.length > 0 ? (
            employeeRows
          ) : (
            <tr>
              <td colSpan="8">No employees found.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default EmployeeList;
