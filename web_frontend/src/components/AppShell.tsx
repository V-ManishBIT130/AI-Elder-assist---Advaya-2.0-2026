import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { navItems } from '../navigation';

const AppShell = () => {
  const location = useLocation();
  const currentPage = navItems.find((item) => location.pathname.startsWith(item.path));

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-head">
          <div className="avatar">R</div>
          <div>
            <p className="patient-name">Raj</p>
            <p className="patient-meta">Clinical Live View</p>
          </div>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `nav-link ${isActive ? 'nav-link-active' : ''}`
              }
            >
              <span className="material-symbols-outlined nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-status">
          <span className="status-dot" />
          <span>ARIA Active</span>
        </div>
      </aside>

      <div className="main-shell">
        <header className="topbar">
          <div>
            <p className="brand">ARIA</p>
            <p className="page-title">{currentPage?.label ?? 'Overview'}</p>
          </div>
          <div className="topbar-right">
            <p className="topbar-note">Updated 2m ago</p>
            <div className="topbar-user">Raj - Live View</div>
          </div>
        </header>

        <main className="page-container">
          <Outlet />
        </main>
      </div>

      <nav className="mobile-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `mobile-nav-link ${isActive ? 'mobile-nav-link-active' : ''}`
            }
          >
            <span className="material-symbols-outlined">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
};

export default AppShell;
