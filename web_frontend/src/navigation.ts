export type NavItem = {
  label: string;
  path: string;
  icon: string;
};

export const navItems: NavItem[] = [
  { label: 'Overview', path: '/overview', icon: 'dashboard' },
  { label: 'Health Trends', path: '/health-trends', icon: 'insights' },
  { label: 'Medications', path: '/medications', icon: 'medical_services' },
  { label: 'Call Logs', path: '/call-logs', icon: 'phone_in_talk' },
  { label: 'Alerts', path: '/alerts', icon: 'notifications_active' },
  { label: 'Settings', path: '/settings', icon: 'settings' },
];
