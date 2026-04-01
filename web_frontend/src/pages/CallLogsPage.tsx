const logs = [
  ['Oct 24, 2023', '09:15 AM', '4m 12s', 88, 92, 'selected'],
  ['Oct 23, 2023', '09:02 AM', '3m 45s', 82, 64, ''],
  ['Oct 22, 2023', '09:10 AM', '5m 02s', 91, 89, ''],
  ['Oct 21, 2023', '09:15 AM', '3m 50s', 71, 85, ''],
  ['Oct 20, 2023', '08:58 AM', '4m 30s', 89, 90, ''],
];

const CallLogsPage = () => {
  return (
    <section className="page-stack">
      <div className="section-heading">
        <h1>Call Logs</h1>
        <p>Daily cognitive and voice biomarker check-ins with clinical summaries.</p>
      </div>

      <div className="call-layout card">
        <aside className="call-list">
          <h2>Check-in History</h2>
          {logs.map((row) => (
            <div key={row[0]} className={`call-item ${row[5]}`}>
              <div>
                <strong>{row[0]}</strong>
                <p>{row[1]} - {row[2]}</p>
              </div>
              <div className="score-pair">
                <span>Cognitive {row[3]}</span>
                <span>Voice {row[4]}</span>
              </div>
            </div>
          ))}
        </aside>

        <div className="call-details">
          <article className="card compact">
            <h3>Voice Biomarker Profile</h3>
            <div className="metric-grid four">
              <div><small>Articulation</small><strong>94%</strong></div>
              <div><small>Pause Frequency</small><strong>High</strong></div>
              <div><small>Jitter</small><strong>0.12ms</strong></div>
              <div><small>Prosody</small><strong>78/100</strong></div>
            </div>
          </article>

          <article className="card compact">
            <h3>Cognitive Assessment Metrics</h3>
            <div className="simple-table">
              <div><span>Short-term Recall</span><strong>85</strong></div>
              <div><span>Working Memory</span><strong className="text-risk">62</strong></div>
              <div><span>Executive Function</span><strong>90</strong></div>
              <div><span>Naming & Fluency</span><strong>94</strong></div>
            </div>
          </article>

          <article className="card compact">
            <h3>Clinical Summary</h3>
            <p>
              Session began with mild tremor markers. Recall remained stable and
              engagement was high. Working memory response latency increased versus
              baseline, indicating possible fatigue impact. Recommend hydration and rest
              follow-up before tomorrow's call.
            </p>
          </article>
        </div>
      </div>
    </section>
  );
};

export default CallLogsPage;
