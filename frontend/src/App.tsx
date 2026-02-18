import { Navigate, Route, Routes, useLocation } from 'react-router-dom';

import { Header } from './components/Header';
import { HomePage } from './pages/HomePage';
import { UploadPage } from './pages/UploadPage';
import { WatchPage } from './pages/WatchPage';

export default function App() {
  const location = useLocation();
  const isWatchPage = location.pathname.startsWith('/watch/');

  return (
    <div className="app-shell">
      <Header />
      <div className="page-layout">
        {!isWatchPage ? (
          <aside className="sidebar">
            <div className="sidebar-item sidebar-item-active">
              <span className="sidebar-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" className="sidebar-svg">
                  <path d="M12 4l8 6v10h-5v-6H9v6H4V10l8-6z" fill="currentColor" />
                </svg>
              </span>
              <span>Home</span>
            </div>
            <div className="sidebar-item">
              <span className="sidebar-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" className="sidebar-svg">
                  <path d="M7 3l10 6-10 6 10 6V3z" fill="currentColor" />
                </svg>
              </span>
              <span>Shorts</span>
            </div>
            <div className="sidebar-item">
              <span className="sidebar-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" className="sidebar-svg">
                  <path d="M3 5h18v14H3V5zm7 3v8l6-4-6-4z" fill="currentColor" />
                </svg>
              </span>
              <span>Subscriptions</span>
            </div>
            <div className="sidebar-item">
              <span className="sidebar-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" className="sidebar-svg">
                  <path d="M4 4h16v16H4V4zm4 4v8h8V8H8z" fill="currentColor" />
                </svg>
              </span>
              <span>Library</span>
            </div>
          </aside>
        ) : null}

        <div className="content-area">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/watch/:id" element={<WatchPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}
