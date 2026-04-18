import { useEffect, useState, useRef } from 'react';
import { getSalaries, getAttendance, createSalary, updateSalary, deleteSalary, createAttendance, updateAttendance, deleteAttendance } from '../services/api';

export default function PayrollPage({ selectedEmployeeId = null }) {
  const [salaries, setSalaries] = useState([]);
  const [attendance, setAttendance] = useState([]);
  const [loading, setLoading] = useState(true);
  const highlightRef = useRef(null);

  // add / edit state
  const [newSalary, setNewSalary] = useState({ employee_id: '', amount: '', effective_date: '' });
  const [editingSalary, setEditingSalary] = useState(null);
  const [salaryEdits, setSalaryEdits] = useState({});

  const [newAttendance, setNewAttendance] = useState({ employee_id: '', work_date: '', work_days: 0, absent_days: 0, leave_days: 0 });
  const [editingAttendance, setEditingAttendance] = useState(null);
  const [attendanceEdits, setAttendanceEdits] = useState({});

  const fmtCurrency = (val, curr = 'VND') => {
    if (val === null || val === undefined || val === '') return '';
    try {
      return new Intl.NumberFormat(undefined, { style: 'currency', currency: curr, maximumFractionDigits: 0 }).format(Number(val));
    } catch (e) {
      return val;
    }
  };

  const fmtDate = (d) => {
    if (!d) return '';
    try { return new Date(d).toLocaleDateString(); } catch (e) { return d; }
  };

  const load = async () => {
    setLoading(true);
    try {
      const [sRes, aRes] = await Promise.all([getSalaries(), getAttendance()]);
      setSalaries(sRes.data || []);
      setAttendance(aRes.data || []);
    } catch (e) {
      console.error('Failed to load payroll', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  useEffect(() => {
    if (!selectedEmployeeId) return;
    const el = document.getElementById(`salary-row-${selectedEmployeeId}`);
    if (el) {
      el.classList.add('highlight-row');
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      setTimeout(() => el.classList.remove('highlight-row'), 3500);
    }
  }, [selectedEmployeeId]);

  const reload = async () => { await load(); };

  if (loading) return <div>Loading payroll data…</div>;

  return (
    <div className="payroll-page">
      <h2>Payroll - Salaries</h2>
      <div className="entity-table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>SalaryID</th>
              <th>EmployeeID</th>
              <th>SalaryMonth</th>
              <th>BaseSalary</th>
              <th>Bonus</th>
              <th>Deductions</th>
              <th>NetSalary</th>
              <th>CreatedAt</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>—</td>
              <td><input type="number" value={newSalary.employee_id} onChange={e => setNewSalary({ ...newSalary, employee_id: e.target.value })} style={{ width: 100 }} /></td>
              <td><input type="date" value={newSalary.effective_date} onChange={e => setNewSalary({ ...newSalary, effective_date: e.target.value })} /></td>
              <td><input type="number" value={newSalary.base_salary ?? newSalary.amount} onChange={e => setNewSalary({ ...newSalary, base_salary: e.target.value })} style={{ width: 140 }} /></td>
              <td><input type="number" value={newSalary.bonus || ''} onChange={e => setNewSalary({ ...newSalary, bonus: e.target.value })} style={{ width: 120 }} /></td>
              <td><input type="number" value={newSalary.deductions || ''} onChange={e => setNewSalary({ ...newSalary, deductions: e.target.value })} style={{ width: 120 }} /></td>
              <td>{fmtCurrency((Number(newSalary.base_salary || newSalary.amount || 0) + Number(newSalary.bonus || 0) - Number(newSalary.deductions || 0)) || '')}</td>
              <td>—</td>
              <td>
                <button className="small" style={{ marginLeft: 8 }} onClick={async () => {
                  try {
                    const base = Number(newSalary.base_salary || newSalary.amount || 0);
                    const bonus = Number(newSalary.bonus || 0);
                    const deductions = Number(newSalary.deductions || 0);
                    const amount = base + bonus - deductions;
                    await createSalary({ employee_id: Number(newSalary.employee_id), base_salary: base, bonus: bonus || null, deductions: deductions || null, amount, effective_date: newSalary.effective_date });
                    setNewSalary({ employee_id: '', amount: '', effective_date: '' });
                    await reload();
                  } catch (e) { alert('Failed to create salary: ' + (e.message || e)); }
                }}>Add</button>
              </td>
            </tr>

            {salaries.length === 0 && (
              <tr><td colSpan={9} className="muted">No salary records found.</td></tr>
            )}

            {salaries.map((s) => {
              const id = s.id;
              return (
                <tr id={`salary-row-${s.employee_id}`} key={id}>
                  <td>{s.id}</td>
                  <td>{s.employee_id}</td>
                  <td>{fmtDate(s.effective_date ?? s.SalaryMonth ?? '')}</td>
                  <td>{fmtCurrency(s.base_salary ?? s.BaseSalary ?? '')}</td>
                  <td>{fmtCurrency(s.bonus ?? s.Bonus ?? '')}</td>
                  <td>{fmtCurrency(s.deductions ?? s.Deductions ?? '')}</td>
                  <td>{fmtCurrency(s.amount ?? s.NetSalary ?? '')}</td>
                  <td>{fmtDate(s.created_at ?? s.CreatedAt ?? '')}</td>
                  <td>
                    <button className="small" onClick={() => { setEditingSalary(id); setSalaryEdits({ base_salary: s.base_salary ?? s.BaseSalary, bonus: s.bonus ?? s.Bonus, deductions: s.deductions ?? s.Deductions, amount: s.amount ?? s.NetSalary, effective_date: (s.effective_date ?? s.SalaryMonth ?? '').slice(0,10) }); }}>Edit</button>
                    <button className="small secondary" style={{ marginLeft: 8 }} onClick={async () => { if (!confirm('Delete this salary?')) return; try { await deleteSalary(id); await reload(); } catch (e) { alert('Delete failed: ' + (e.message || e)); } }}>Delete</button>
                    {editingSalary === id && (
                      <div style={{ marginTop: 6 }}>
                        <input type="number" value={salaryEdits.base_salary ?? ''} onChange={e => setSalaryEdits({ ...salaryEdits, base_salary: Number(e.target.value) })} style={{ width: 120 }} />
                        <input type="number" value={salaryEdits.bonus ?? ''} onChange={e => setSalaryEdits({ ...salaryEdits, bonus: Number(e.target.value) })} style={{ width: 120, marginLeft: 8 }} />
                        <input type="number" value={salaryEdits.deductions ?? ''} onChange={e => setSalaryEdits({ ...salaryEdits, deductions: Number(e.target.value) })} style={{ width: 120, marginLeft: 8 }} />
                        <input type="date" value={salaryEdits.effective_date ?? ''} onChange={e => setSalaryEdits({ ...salaryEdits, effective_date: e.target.value })} style={{ marginLeft: 8 }} />
                        <button className="small" style={{ marginLeft: 8 }} onClick={async () => { try { await updateSalary(id, salaryEdits); setEditingSalary(null); setSalaryEdits({}); await reload(); } catch (e) { alert('Save failed: ' + (e.message || e)); } }}>Save</button>
                        <button className="small secondary" style={{ marginLeft: 8 }} onClick={() => { setEditingSalary(null); setSalaryEdits({}); }}>Cancel</button>
                      </div>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div style={{ height: 24 }} />

      <h2>Payroll - Attendance</h2>
      <div className="entity-table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Employee ID</th>
              <th>Date</th>
              <th>Status</th>
              <th>Hours</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><input type="number" value={newAttendance.employee_id} onChange={e => setNewAttendance({ ...newAttendance, employee_id: e.target.value })} style={{ width: 120 }} /></td>
              <td><input type="date" value={newAttendance.work_date} onChange={e => setNewAttendance({ ...newAttendance, work_date: e.target.value })} /></td>
              <td>
                <input type="number" value={newAttendance.work_days} onChange={e => setNewAttendance({ ...newAttendance, work_days: Number(e.target.value) })} style={{ width: 80 }} />
              </td>
              <td>
                <input type="number" value={newAttendance.leave_days} onChange={e => setNewAttendance({ ...newAttendance, leave_days: Number(e.target.value) })} style={{ width: 80 }} />
                <button className="small" style={{ marginLeft: 8 }} onClick={async () => {
                  try {
                    await createAttendance({ employee_id: Number(newAttendance.employee_id), work_date: newAttendance.work_date, work_days: Number(newAttendance.work_days), leave_days: Number(newAttendance.leave_days), absent_days: Number(newAttendance.absent_days) });
                    setNewAttendance({ employee_id: '', work_date: '', work_days: 0, absent_days: 0, leave_days: 0 });
                    await reload();
                  } catch (e) { alert('Failed to create attendance: ' + (e.message || e)); }
                }}>Add</button>
              </td>
            </tr>

            {attendance.length === 0 && (
              <tr><td colSpan={6} className="muted">No attendance records found.</td></tr>
            )}

            {attendance.map((a) => {
              const id = a.id;
              return (
                <tr key={id || `${a.employee_id}-${a.work_date}`}>
                  <td>{a.id}</td>
                  <td>{a.employee_id}</td>
                  <td>{fmtDate(a.work_date ?? a.AttendanceMonth ?? '')}</td>
                  <td>{a.work_days ?? a.WorkDays ?? a.hours ?? 0}</td>
                  <td>{a.absent_days ?? a.AbsentDays ?? 0}</td>
                  <td>{a.leave_days ?? a.LeaveDays ?? a.leave_hours ?? 0}</td>
                  <td>{fmtDate(a.created_at ?? a.CreatedAt ?? '')}</td>
                  <td>
                    <button className="small" onClick={() => { setEditingAttendance(id); setAttendanceEdits({ employee_id: a.employee_id, work_date: (a.work_date || a.AttendanceMonth || '').slice(0, 10), work_days: a.work_days || a.WorkDays || a.hours || 0, absent_days: a.absent_days || a.AbsentDays || 0, leave_days: a.leave_days || a.LeaveDays || a.leave_hours || 0 }); }}>Edit</button>
                    <button className="small secondary" style={{ marginLeft: 8 }} onClick={async () => { if (!confirm('Delete this attendance?')) return; try { await deleteAttendance(a.id); await reload(); } catch (e) { alert('Delete failed: ' + (e.message || e)); } }}>Delete</button>
                    {editingAttendance === id && (
                      <div style={{ marginTop: 6 }}>
                        <input type="number" value={attendanceEdits.work_days ?? ''} onChange={e => setAttendanceEdits({ ...attendanceEdits, work_days: Number(e.target.value) })} style={{ width: 80 }} />
                        <input type="number" value={attendanceEdits.absent_days ?? ''} onChange={e => setAttendanceEdits({ ...attendanceEdits, absent_days: Number(e.target.value) })} style={{ width: 80, marginLeft: 8 }} />
                        <input type="number" value={attendanceEdits.leave_days ?? ''} onChange={e => setAttendanceEdits({ ...attendanceEdits, leave_days: Number(e.target.value) })} style={{ width: 80, marginLeft: 8 }} />
                        <input type="date" value={attendanceEdits.work_date ?? ''} onChange={e => setAttendanceEdits({ ...attendanceEdits, work_date: e.target.value })} style={{ marginLeft: 8 }} />
                        <button className="small" style={{ marginLeft: 8 }} onClick={async () => { try { await updateAttendance(id, attendanceEdits); setEditingAttendance(null); setAttendanceEdits({}); await reload(); } catch (e) { alert('Save failed: ' + (e.message || e)); } }}>Save</button>
                        <button className="small secondary" style={{ marginLeft: 8 }} onClick={() => { setEditingAttendance(null); setAttendanceEdits({}); }}>Cancel</button>
                      </div>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
