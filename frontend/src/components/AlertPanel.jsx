
import { useEffect, useState, useRef } from 'react';
import { getAlerts } from '../services/api';

function AlertPanel() {
  const [alerts, setAlerts] = useState(null);
  const [error, setError] = useState(null);
  const [openType, setOpenType] = useState(null); // 'anniversaries' | 'abnormal_salaries' | 'excessive_leave'
  const panelRef = useRef();

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await getAlerts();
        setAlerts(response.data);
      } catch (err) {
        setError('Unable to load alerts.');
      }
    };
    fetchAlerts();
  }, []);

  // close dropdown when clicking outside
  useEffect(() => {
    function onDoc(e) {
      if (panelRef.current && !panelRef.current.contains(e.target)) {
        setOpenType(null);
      }
    }
    document.addEventListener('click', onDoc);
    return () => document.removeEventListener('click', onDoc);
  }, []);

  const openDetails = (type) => {
    setOpenType((t) => (t === type ? null : type));
  };

  const renderList = (type) => {
    if (!alerts) return null;
    const items = alerts[type] || [];
    if (items.length === 0) return <div className="alert-empty">No items</div>;
    return (
      <ul className="alert-list">
        {items.slice(0, 8).map((it, idx) => (
          <li key={idx} className="alert-item">
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
              <div>
                {it.name || `#${it.employee_id}` || it.amount || JSON.stringify(it)}
                {it.hire_date && <span className="muted"> — {it.hire_date}</span>}
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                {it.employee_id && (
                  <button
                    className="small"
                    onClick={() => window.dispatchEvent(new CustomEvent('navigate', { detail: { tab: 'payroll', employeeId: it.employee_id } }))}
                  >
                    View
                  </button>
                )}
              </div>
            </div>
          </li>
        ))}
        {items.length > 8 && <li className="alert-more">And {items.length - 8} more...</li>}
      </ul>
    );
  };

  return (
    <section className="alerts-bar" ref={panelRef}>
      <div className="alerts-title">Alerts</div>
      {error && <div className="alert-error">{error}</div>}
      {alerts ? (
        <div className="alerts-summary">
          <button className="alert-pill info" onClick={() => openDetails('anniversaries')}>
            Anniversaries: <strong>{alerts.anniversaries.length}</strong>
          </button>

          <button className="alert-pill danger" onClick={() => openDetails('abnormal_salaries')}>
            Abnormal Salaries: <strong>{alerts.abnormal_salaries.length}</strong>
          </button>

          <button className="alert-pill warn" onClick={() => openDetails('excessive_leave')}>
            Excessive Leave: <strong>{alerts.excessive_leave.length}</strong>
          </button>

          {openType && (
            <div className="alert-dropdown">
              <div className="alert-dropdown-head">
                <strong>{openType.replace(/_/g, ' ')}</strong>
                <button className="close-x" onClick={() => setOpenType(null)}>×</button>
              </div>
              <div className="alert-dropdown-body">{renderList(openType)}</div>
            </div>
          )}
        </div>
      ) : (
        <div>Loading alerts...</div>
      )}
    </section>
  );
}

export default AlertPanel;
