import { useMemo } from 'react';
import { PieChart, Pie, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

function EmployeeDashboard({ employees }) {
  // Calculate stats
  const stats = useMemo(() => {
    const total = employees.length;
    
    // Status distribution
    const statusCounts = {};
    employees.forEach((emp) => {
      const status = emp.status || 'active';
      statusCounts[status] = (statusCounts[status] || 0) + 1;
    });
    const statusData = Object.entries(statusCounts).map(([status, count]) => ({
      name: status.charAt(0).toUpperCase() + status.slice(1),
      value: count,
    }));

    // Department distribution
    const deptCounts = {};
    employees.forEach((emp) => {
      const dept = emp.department_id ? `Dept ${emp.department_id}` : 'No Department';
      deptCounts[dept] = (deptCounts[dept] || 0) + 1;
    });
    const deptData = Object.entries(deptCounts)
      .map(([dept, count]) => ({ name: dept, value: count }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 10); // Top 10 departments

    // Position distribution
    const posCounts = {};
    employees.forEach((emp) => {
      const pos = emp.position_id ? `Pos ${emp.position_id}` : 'No Position';
      posCounts[pos] = (posCounts[pos] || 0) + 1;
    });
    const posData = Object.entries(posCounts)
      .map(([pos, count]) => ({ name: pos, value: count }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 10); // Top 10 positions

    return {
      total,
      statusData,
      deptData,
      posData,
    };
  }, [employees]);

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ marginBottom: '40px' }}>
        <h3 style={{ marginBottom: '16px' }}>Employee Overview</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <div style={{ padding: '20px', background: '#eef2ff', borderRadius: '16px', border: '1px solid #c7d2fe' }}>
            <div style={{ fontSize: '0.95rem', color: '#64748b', marginBottom: '10px' }}>Total Employees</div>
            <div style={{ fontSize: '2.2rem', fontWeight: '800', color: '#1e3a8a' }}>{stats.total}</div>
          </div>
        </div>
      </div>

      {/* Status Distribution - Pie Chart */}
      {stats.statusData.length > 0 && (
        <div style={{ marginBottom: '40px', background: '#fff', padding: '24px', borderRadius: '16px', border: '1px solid #e5e7eb' }}>
          <h4 style={{ marginTop: 0, marginBottom: '24px', fontSize: '1.1rem' }}>Employee Status Distribution</h4>
          <ResponsiveContainer width="100%" height={550}>
            <PieChart>
              <Pie
                data={stats.statusData}
                cx="50%"
                cy="45%"
                labelLine={true}
                label={({ name, percent }) => `${name} ${Math.round(percent * 100)}%`}
                outerRadius={110}
                fill="#8884d8"
                dataKey="value"
              >
                {stats.statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`${value}`, 'Employees']} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Department Distribution - Bar Chart */}
      {stats.deptData.length > 0 && (
        <div style={{ marginBottom: '40px', background: '#fff', padding: '18px', borderRadius: '16px', border: '1px solid #e5e7eb' }}>
          <h4 style={{ marginTop: 0, marginBottom: '18px' }}>Employees by Department</h4>
          <ResponsiveContainer width="100%" height={340}>
            <BarChart data={stats.deptData} margin={{ top: 10, right: 20, left: -10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} interval={0} angle={-25} textAnchor="end" height={70} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip formatter={(value) => [`${value}`, 'Employees']} />
              <Bar dataKey="value" fill="#3b82f6" radius={[10, 10, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Position Distribution - Bar Chart */}
      {stats.posData.length > 0 && (
        <div style={{ marginBottom: '40px', background: '#fff', padding: '18px', borderRadius: '16px', border: '1px solid #e5e7eb' }}>
          <h4 style={{ marginTop: 0, marginBottom: '18px' }}>Employees by Position</h4>
          <ResponsiveContainer width="100%" height={340}>
            <BarChart data={stats.posData} margin={{ top: 10, right: 20, left: -10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} interval={0} angle={-25} textAnchor="end" height={70} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip formatter={(value) => [`${value}`, 'Employees']} />
              <Bar dataKey="value" fill="#10b981" radius={[10, 10, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

export default EmployeeDashboard;
