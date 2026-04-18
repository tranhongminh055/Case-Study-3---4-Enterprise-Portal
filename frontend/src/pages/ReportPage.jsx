import { useEffect, useState } from 'react';
import { getReports, getAlerts, getEmployees, updateEmployee } from '../services/api';

function ReportPage() {
  const [reports, setReports] = useState([]);
  const [alerts, setAlerts] = useState(null);
  const [employees, setEmployees] = useState([]);
  const [broken, setBroken] = useState([]);
  const [error, setError] = useState(null);

  const loadReports = async () => {
    try {
      const [reportResponse, alertResponse, empResponse] = await Promise.all([getReports(), getAlerts(), getEmployees()]);
      setReports(reportResponse.data);
      setAlerts(alertResponse.data);
      setEmployees(empResponse.data || []);
      // detect broken names containing replacement char or question marks from encoding issues
      const problem = (empResponse.data || []).filter(e => {
        const name = (e.full_name || e.name || '').toString();
        return name.includes('?') || name.includes('�');
      }).map(e => ({ ...e, editValue: (e.full_name || e.name || '') }));
      setBroken(problem);
      setError(null);
    } catch (err) {
      setError('Unable to load reports and alerts.');
    }
  };

  useEffect(() => {
    loadReports();
  }, []);

  return (
    <section className="page-section">
      <h2>Reports & Alerts</h2>
      {error && <div className="flash-message">{error}</div>}
      <div className="form-actions" style={{ marginTop: 8 }}>
        <button className="small" onClick={() => {
          const blob = new Blob([JSON.stringify(reports, null, 2)], { type: 'application/json' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url; a.download = 'employee_report.json'; a.click();
          URL.revokeObjectURL(url);
        }}>Export JSON</button>
        <button className="small secondary" onClick={() => {
          if (!reports || reports.length === 0) return;
          const header = ['employee_id','name','email','salary','bonus','deductions','attendance_count','attendance_dates','hire_date'];
          const rows = reports.map(r => {
            const dates = (r.attendance || []).map(a => a.date || '').join(';');
            return [r.employee_id, r.name, r.email, r.salary ?? '', r.bonus ?? '', r.deductions ?? '', (r.attendance || []).length, `"${dates.replace(/"/g,'""')}"`, r.hire_date || ''];
          });
          const csv = [header.join(','), ...rows.map(r => r.join(','))].join('\n');
          const blob = new Blob([csv], { type: 'text/csv' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a'); a.href = url; a.download = 'employee_report.csv'; a.click(); URL.revokeObjectURL(url);
        }}>Export CSV</button>

        <button className="small" onClick={() => {
          // simple Excel export using HTML table (widely supported by Excel)
          if (!reports || reports.length === 0) return;
          let html = '<table><thead><tr>';
          const cols = ['ID','Name','Email','Salary','Bonus','Deductions','AttendanceCount','AttendanceDates','HireDate'];
          html += cols.map(c => `<th>${c}</th>`).join('') + '</tr></thead><tbody>';
          reports.forEach(r => {
            const dates = (r.attendance || []).map(a => a.date || '').join(';');
            html += '<tr>' + [r.employee_id, r.name, r.email, r.salary ?? '', r.bonus ?? '', r.deductions ?? '', (r.attendance || []).length, dates, r.hire_date || ''].map(c => `<td>${c}</td>`).join('') + '</tr>';
          });
          html += '</tbody></table>';
          const blob = new Blob(['\ufeff' + html], { type: 'application/vnd.ms-excel' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a'); a.href = url; a.download = 'employee_report.xls'; a.click(); URL.revokeObjectURL(url);
        }}>Export Excel</button>
      </div>
      {broken.length > 0 && (
        <div className="card full-card" style={{ marginTop: 16 }}>
          <h3>Fix Broken Names</h3>
          <p style={{ marginTop: 0 }}>Found <strong>{broken.length}</strong> employees with possible encoding issues. Edit and Save to correct.</p>
          <table className="data-table">
            <thead>
              <tr><th>ID</th><th>Current Name</th><th>Fix</th><th>Action</th></tr>
            </thead>
            <tbody>
              {broken.map((row) => (
                <tr key={row.employee_id || row.id} id={`fix-row-${row.employee_id || row.id}`}>
                  <td>{row.employee_id || row.id}</td>
                  <td className="name-cell">{row.full_name || row.name}</td>
                  <td style={{ width: 420 }}>
                    <input type="text" value={row.editValue} onChange={e => {
                      const nv = e.target.value;
                      setBroken(prev => prev.map(p => (p.employee_id === row.employee_id ? { ...p, editValue: nv } : p)));
                    }} style={{ width: '100%' }} />
                  </td>
                  <td>
                    <button className="small" onClick={async () => {
                      const id = row.employee_id || row.id;
                      try {
                        await updateEmployee(id, { full_name: row.editValue });
                        // reflect change locally
                        setBroken(prev => prev.filter(p => (p.employee_id || p.id) !== id));
                      } catch (e) {
                        alert('Failed to save: ' + (e.message || e));
                      }
                    }}>Save</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div className="page-grid">
        <div className="card full-card">
          <h3>Combined Employee Report</h3>
          <table className="data-table">
            <thead>
              <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Salary</th>
                      <th>Attendance Records</th>
                    </tr>
            </thead>
            <tbody>
              {reports.map((row) => (
                <tr key={row.employee_id}>
                  <td>{row.employee_id}</td>
                  <td className="name-cell">{row.name}</td>
                  <td>{row.email}</td>
                  <td>{row.salary ?? 'N/A'}</td>
                  <td>{row.attendance.length}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {alerts && (
          <div className="card full-card">
            <h3>Alerts</h3>
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
              <div className="alert-pill info">Anniversaries: <strong>{alerts.anniversaries.length}</strong></div>
              <div className="alert-pill danger">Abnormal Salaries: <strong>{alerts.abnormal_salaries.length}</strong></div>
              <div className="alert-pill warn">Excessive Leave: <strong>{alerts.excessive_leave.length}</strong></div>
            </div>

            <div style={{ marginTop: 12 }}>
              <h4 style={{ margin: '8px 0' }}>Recent Abnormal Salaries</h4>
              <ul style={{ margin: 0, paddingLeft: 16 }}>
                {(alerts.abnormal_salaries || []).slice(0,5).map((a, idx) => (
                  <li key={idx}>Employee #{a.employee_id} — {a.amount?.toLocaleString ? a.amount.toLocaleString() : a.amount} ({a.effective_date})</li>
                ))}
                {(alerts.abnormal_salaries || []).length === 0 && <li>No abnormal salary alerts</li>}
              </ul>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

export default ReportPage;
