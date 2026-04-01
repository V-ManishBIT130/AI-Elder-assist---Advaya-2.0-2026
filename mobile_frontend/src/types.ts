export type AppTab = 'home' | 'medications' | 'emergency';

export interface ScreenNavigationProps {
  activeTab: AppTab;
  onNavigate: (tab: AppTab) => void;
}
