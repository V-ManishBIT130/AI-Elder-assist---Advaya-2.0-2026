# Web Frontend Implementation Notes

## Purpose
Create a new `web_frontend` React application that converts the provided warm-intelligence HTML designs into a responsive, routed caregiver dashboard.

## Source HTML Mapped
- `web_frontend_designs/overview_warm_intelligence/code.html`
- `web_frontend_designs/health_trends_warm_intelligence/code.html`
- `web_frontend_designs/medications_warm_intelligence/code.html`
- `web_frontend_designs/call_logs_warm_intelligence/code.html`
- `web_frontend_designs/alerts_warm_intelligence/code.html`
- `web_frontend_designs/settings_warm_intelligence/code.html`

## Stack
- React + TypeScript (Vite)
- React Router (`react-router-dom`)
- CSS custom design system (warm palette + typography)
- Material Symbols webfont icons

## Folder Structure
- `src/components/AppShell.tsx`:
  - Shared responsive shell with sidebar, top bar, and mobile navbar
  - Central nav routing for all pages
- `src/navigation.ts`:
  - Single source of truth for nav labels, paths, and icons
- `src/pages/OverviewPage.tsx`
- `src/pages/HealthTrendsPage.tsx`
- `src/pages/MedicationsPage.tsx`
- `src/pages/CallLogsPage.tsx`
- `src/pages/AlertsPage.tsx`
- `src/pages/SettingsPage.tsx`
- `src/App.tsx`:
  - Route registration and default redirect
- `src/main.tsx`:
  - BrowserRouter integration
- `src/index.css`:
  - Global responsive style system and page-level component styles

## Routing
All nav buttons now route to the corresponding pages:
- `/overview`
- `/health-trends`
- `/medications`
- `/call-logs`
- `/alerts`
- `/settings`

Desktop:
- Left sidebar includes all 6 links.

Mobile:
- Bottom nav includes all 6 links in horizontal scroll.

## Responsive Design Decisions
- Sidebar hidden below tablet/mobile breakpoints.
- Sticky top bar retained across pages.
- Mobile bottom nav added for quick page switching.
- Complex desktop grids collapse to single-column layout on smaller screens.
- Alert table switches to stacked rows on narrow screens.
- Typography and spacing follow a warm editorial style while preserving readability.

## Commands Executed
```bash
npm create vite@latest web_frontend -- --template react
npm install
npm install react-router-dom
npm run build
```

## Verification
- TypeScript diagnostics: no errors.
- Vite build: success.
- Navigation mapping validated in route configuration and shell nav.

## Run
```bash
cd web_frontend
npm install
npm run dev
```

## Notes
- This version prioritizes responsive structure and page connectivity.
- Next enhancement can include chart interactivity, API wiring, and persistent state for filters/toggles.
