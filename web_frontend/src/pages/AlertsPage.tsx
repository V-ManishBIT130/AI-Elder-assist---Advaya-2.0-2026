const alerts = [
  ['HIGH', 'Systolic BP threshold exceeded (>180 mmHg)', 'Sensor_A1', '08:42 AM', 'Unresolved'],
  ['HIGH', 'Missed dosage: Metformin 500mg', 'Dispense_02', '08:15 AM', 'Unresolved'],
  ['MEDIUM', 'Irregular heart rate detected (Tachycardia)', 'Bio_Wear_4', '07:58 AM', 'Pending'],
  ['MEDIUM', 'Mobility decrease: 24hr gait analysis', 'Vision_S1', '06:30 AM', 'Pending'],
  ['LOW', 'Battery low: Primary gateway node', 'System', '05:12 AM', 'Pending'],
  ['LOW', 'Room temperature anomaly: Master Bedroom', 'Env_302', '04:45 AM', 'Pending'],
];

const AlertsPage = () => {
  return (
    <section className="page-stack">
      <div className="section-heading">
        <h1>Full Alert History</h1>
        <p>Urgency-ordered management so no critical event is buried in noise.</p>
      </div>

      <div className="filter-row">
        <div className="segmented">
          <button className="active">All</button>
          <button>High</button>
          <button>Medium</button>
          <button>Low</button>
        </div>
        <div className="segmented">
          <button className="active">Pending</button>
          <button>Resolved</button>
        </div>
      </div>

      <article className="card alerts-table-wrap">
        <div className="alerts-table header">
          <span>Severity</span>
          <span>Title</span>
          <span>Agent</span>
          <span>Time</span>
          <span>Status</span>
          <span>Action</span>
        </div>
        {alerts.map((a) => (
          <div key={a[1]} className={`alerts-table row row-${a[0].toLowerCase()}`}>
            <span className="severity">{a[0]}</span>
            <span>{a[1]}</span>
            <span>{a[2]}</span>
            <span>{a[3]}</span>
            <span>{a[4]}</span>
            <button>Acknowledge</button>
          </div>
        ))}
      </article>
    </section>
  );
};

export default AlertsPage;
