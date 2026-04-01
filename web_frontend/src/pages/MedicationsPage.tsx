const days = Array.from({ length: 30 }, (_, i) => i + 1);

const MedicationsPage = () => {
  return (
    <section className="page-stack">
      <div className="section-heading">
        <h1>Medication Management</h1>
        <p>Adherence intelligence, interaction safety, and refill readiness in one view.</p>
      </div>

      <div className="two-col">
        <div className="stack">
          <article className="card">
            <h2>Today's Schedule</h2>
            <div className="schedule-list">
              <div className="schedule-item ok">
                <div>
                  <p className="time">08:00 AM - Morning</p>
                  <h3>Atorvastatin 20mg</h3>
                  <p>Take with water before breakfast.</p>
                </div>
                <span className="status-tag">Administered</span>
              </div>
              <div className="schedule-item risk">
                <div>
                  <p className="time">12:30 PM - Afternoon</p>
                  <h3>Metformin 500mg</h3>
                  <p>Must be taken during or after a meal.</p>
                </div>
                <span className="status-tag">Missed</span>
              </div>
              <div className="schedule-item pending">
                <div>
                  <p className="time">09:00 PM - Evening</p>
                  <h3>Lisinopril 10mg</h3>
                  <p>Regular nightly dosage.</p>
                </div>
                <span className="status-tag">Upcoming</span>
              </div>
            </div>
          </article>

          <article className="card warn-card">
            <h2>Drug Interaction Warning</h2>
            <p>
              Potential interaction detected between Lisinopril and Ibuprofen. This
              combination may reduce kidney function efficiency when taken together.
            </p>
            <button className="primary-btn">Mark reviewed</button>
          </article>
        </div>

        <div className="stack">
          <article className="card">
            <h2>Adherence Calendar</h2>
            <div className="calendar-grid">
              {days.map((day) => (
                <span
                  key={day}
                  className={`calendar-dot ${day === 4 || day === 12 ? 'missed' : day > 22 ? 'future' : 'taken'}`}
                />
              ))}
            </div>
          </article>

          <article className="card">
            <h2>Inventory Status</h2>
            <div className="inventory-row">
              <div>
                <p>Atorvastatin</p>
                <small>22 days remaining</small>
              </div>
              <div className="meter"><span style={{ width: '70%' }} /></div>
            </div>
            <div className="inventory-row">
              <div>
                <p>Metformin</p>
                <small>Refill needed</small>
              </div>
              <div className="meter"><span style={{ width: '12%' }} className="risk" /></div>
            </div>
            <div className="inventory-row">
              <div>
                <p>Lisinopril</p>
                <small>14 days remaining</small>
              </div>
              <div className="meter"><span style={{ width: '45%' }} /></div>
            </div>
            <button className="ghost-btn">Request Refills</button>
          </article>
        </div>
      </div>
    </section>
  );
};

export default MedicationsPage;
