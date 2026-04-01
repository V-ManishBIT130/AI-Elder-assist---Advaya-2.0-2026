const toggles = [
  'Critical Alerts',
  'Medication Reminders',
  'Daily Summaries',
  'Movement Activity',
  'Call Log Updates',
  'System Maintenance',
];

const SettingsPage = () => {
  return (
    <section className="page-stack">
      <div className="section-heading">
        <h1>Clinical Settings</h1>
        <p>Form-driven configuration for profile, emergency contacts, and preferences.</p>
      </div>

      <div className="stack">
        <article className="card">
          <h2>Patient Profile</h2>
          <div className="info-grid">
            <div><small>Full Legal Name</small><p>Raj</p></div>
            <div><small>Date of Birth</small><p>May 14, 1948</p></div>
            <div><small>Primary Language</small><p>English / Hindi</p></div>
            <div><small>Blood Type</small><p>A+</p></div>
            <div><small>Clinic ID</small><p>#8821-XQ-90</p></div>
            <div><small>Residence Status</small><p>Independent / Assisted Remote</p></div>
          </div>
        </article>

        <article className="card">
          <h2>Emergency Contacts</h2>
          <div className="contact-row">
            <div>
              <p>Asha Raj</p>
              <small>Daughter - +91 98765 43210</small>
            </div>
            <button>Edit</button>
          </div>
          <div className="contact-row">
            <div>
              <p>Dr. Ananya Mehta</p>
              <small>Primary Physician - +91 98111 22446</small>
            </div>
            <button>Edit</button>
          </div>
        </article>

        <article className="card">
          <h2>Notification Preferences</h2>
          <div className="toggle-grid">
            {toggles.map((label, idx) => (
              <label className="toggle-row" key={label}>
                <span>{label}</span>
                <input type="checkbox" defaultChecked={idx !== 3 && idx !== 4} />
              </label>
            ))}
          </div>
        </article>
      </div>
    </section>
  );
};

export default SettingsPage;
