import { Navigate, NavLink, Route, Routes, useLocation } from 'react-router-dom';

import { Header } from './components/Header';
import { HomePage } from './pages/HomePage';
import { SubscriptionsPage } from './pages/SubscriptionsPage';
import { UploadPage } from './pages/UploadPage';
import { UsersPage } from './pages/UsersPage';
import { WatchPage } from './pages/WatchPage';

function SidebarItem({ to, label, iconPath }: { to: string; label: string; iconPath: string }) {
  return (
    <NavLink to={to} className={({ isActive }) => (isActive ? 'sidebar-item sidebar-item-active' : 'sidebar-item')}>
      <span className="sidebar-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" className="sidebar-svg">
          <path d={iconPath} fill="currentColor" />
        </svg>
      </span>
      <span>{label}</span>
    </NavLink>
  );
}

export default function App() {
  const location = useLocation();
  const isWatchPage = location.pathname.startsWith('/watch/');

  return (
    <div className="app-shell">
      <Header />
      <div className="page-layout">
        {!isWatchPage ? (
          <aside className="sidebar">
            <SidebarItem to="/" label="Home" iconPath="M12 4l8 6v10h-5v-6H9v6H4V10l8-6z" />
            <SidebarItem to="/subscriptions" label="Subscriptions" iconPath="M3 5h18v14H3V5zm7 3v8l6-4-6-4z" />
            <SidebarItem to="/users" label="Users" iconPath="M12 12a5 5 0 1 0-5-5 5 5 0 0 0 5 5zm0 2c-4.4 0-8 2-8 4.5V21h16v-2.5c0-2.5-3.6-4.5-8-4.5z" />
            <SidebarItem to="/upload" label="Upload" iconPath="M19 11h-6V5h-2v6H5v2h6v6h2v-6h6z" />
          </aside>
        ) : null}

        <div className="content-area">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/subscriptions" element={<SubscriptionsPage />} />
            <Route path="/users" element={<UsersPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/watch/:id" element={<WatchPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}
