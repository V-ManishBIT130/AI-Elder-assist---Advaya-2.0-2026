const agentLogs = [
  ['11:42:04', 'AGENT_VOICE', 'Detecting vocal tremors... Stability confirmed.'],
  ['11:15:30', 'AGENT_VISION', 'Terrace movement detected. Sunlight exposure 12 min.'],
  ['10:45:12', 'AGENT_BIOMETRIC', 'Heart-rate variability baseline updated.'],
  ['10:02:55', 'AGENT_COMM', 'Outbound call started. Recipient: Asha.'],
  ['09:30:11', 'AGENT_VOICE', 'Morning greeting analysis complete. Mood: Positive.'],
  ['08:15:44', 'AGENT_VISION', 'Kitchen activity detected. Breakfast sequence normal.'],
];

const OverviewPage = () => {
  return (
    <section className="page-stack">
      <div className="section-heading">
        <h1>Caregiver Overview</h1>
        <p>Warm-intelligence dashboard for daily clinical context and trend monitoring.</p>
      </div>

      <div className="kpi-grid">
        <article className="kpi-card">
          <p>Fall Risk Index</p>
          <h3>34</h3>
          <span className="pill pill-ok">Low</span>
        </article>
        <article className="kpi-card">
          <p>Cognitive Score</p>
          <h3>71</h3>
          <span className="pill">Baseline</span>
        </article>
        <article className="kpi-card">
          <p>Social Engagement</p>
          <h3>62%</h3>
          <span className="pill">Stable</span>
        </article>
        <article className="kpi-card">
          <p>Sleep Quality</p>
          <h3>5.2 hrs</h3>
          <span className="pill pill-risk">Below Avg</span>
        </article>
      </div>

      <div className="two-col">
        <article className="card narrative-card">
          <h2>Narrative Summary</h2>
          <p>
            Raj woke at 6:45 AM with slightly restless sleep but completed his
            morning routine independently. During the 10:15 AM call, voice stability was
            high and stress markers were low. Cognitive focus during his puzzle session
            remained above his 30-day moving average.
          </p>
          <div className="alert-note">
            <span className="material-symbols-outlined">task_alt</span>
            <span>Action needed: Confirm Vitamin D3 refill before 5:00 PM.</span>
          </div>

          <div className="log-list">
            <h3>Agent Activity Log</h3>
            {agentLogs.map((log) => (
              <div key={log[0]} className="log-item">
                <span>{log[0]}</span>
                <strong>{log[1]}</strong>
                <span>{log[2]}</span>
              </div>
            ))}
          </div>
        </article>

        <aside className="stack">
          <article className="card">
            <h2>Voice Clarity Trend</h2>
            <div className="bar-chart">
              {[55, 62, 58, 70, 81, 76].map((v, i) => (
                <span key={i} style={{ height: `${v}%` }} />
              ))}
            </div>
          </article>

          <article className="card">
            <h2>Cognitive Focus</h2>
            <div className="line-chart">
              <svg viewBox="0 0 400 130" preserveAspectRatio="none">
                <path d="M0,110 C80,90 120,105 180,70 C250,32 300,45 400,26" />
              </svg>
            </div>
          </article>

          <article className="card">
            <h2>Recent Alerts</h2>
            <div className="mini-alert mini-alert-high">
              Sleep duration below threshold: 5h 12m
            </div>
            <div className="mini-alert mini-alert-med">
              Upcoming specialist visit tomorrow at 2:00 PM
            </div>
          </article>
        </aside>
      </div>
    </section>
  );
};

export default OverviewPage;
