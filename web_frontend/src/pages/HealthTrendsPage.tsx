const HealthTrendsPage = () => {
  return (
    <section className="page-stack">
      <div className="section-heading heading-row">
        <div>
          <h1>Health Trends</h1>
          <p>Pattern-based view across mobility, sleep, social engagement, and risk.</p>
        </div>
        <div className="segmented">
          <button>7 days</button>
          <button className="active">30 days</button>
          <button>90 days</button>
        </div>
      </div>

      <article className="card wide-hero">
        <div className="wide-hero-grid">
          <div>
            <h2>Fall Risk Probability</h2>
            <div className="trend-chart">
              <svg viewBox="0 0 1000 280" preserveAspectRatio="none">
                <path d="M0,235 L100,228 L200,246 L300,205 L400,178 L500,212 L600,142 L700,92 L800,150 L900,194 L1000,184" />
              </svg>
            </div>
          </div>
          <aside>
            <h3>Interpretation</h3>
            <p>
              Mid-month spike aligns with a medication adjustment window. Trend has started
              stabilizing with improved morning movement consistency.
            </p>
          </aside>
        </div>
      </article>

      <article className="card">
        <h2>14-Night Sleep Restfulness</h2>
        <div className="sleep-chart">
          {[85, 70, 75, 40, 80, 90, 85, 35, 75, 78, 82, 65, 70, 88].map((v, i) => (
            <span key={i} style={{ height: `${v}%` }} className={v < 50 ? 'low' : ''} />
          ))}
        </div>
        <p className="caption">
          Two low-rest nights were detected. Overall sleep efficiency remains stable at 88%.
        </p>
      </article>

      <div className="two-col">
        <article className="card">
          <h2>Social Wellness Index</h2>
          <div className="line-chart">
            <svg viewBox="0 0 400 130" preserveAspectRatio="none">
              <path d="M0,92 C70,106 110,48 170,58 C230,72 282,26 350,44 C382,55 400,48 400,48" />
            </svg>
          </div>
          <p className="caption">Peaks align with family calls and weekly bridge group routines.</p>
        </article>

        <article className="card">
          <h2>Morning Activity Comparison</h2>
          <div className="compare-bars">
            <div>
              <span className="bar muted" style={{ height: '68%' }} />
              <p>Last week</p>
            </div>
            <div>
              <span className="bar" style={{ height: '82%' }} />
              <p>This week</p>
            </div>
          </div>
          <p className="caption">Morning vitality is up 12% after physical therapy schedule changes.</p>
        </article>
      </div>
    </section>
  );
};

export default HealthTrendsPage;
