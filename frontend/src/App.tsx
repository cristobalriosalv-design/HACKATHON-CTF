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
            <div className="sidebar-item sidebar-item-active">Home</div>
            <div className="sidebar-item">Shorts</div>
            <div className="sidebar-item">Subscriptions</div>
            <div className="sidebar-item">Library</div>
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
