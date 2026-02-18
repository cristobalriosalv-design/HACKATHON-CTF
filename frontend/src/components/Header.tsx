import { Link } from 'react-router-dom';

export function Header() {
  return (
    <header className="header">
      <div className="header-left">
        <button className="icon-btn" aria-label="Menu">
          <span />
          <span />
          <span />
        </button>
        <Link to="/" className="brand">
          <span className="brand-badge">
            <span className="brand-play" />
          </span>
          <span className="brand-text">YouTube</span>
        </Link>
      </div>

      <div className="search-wrap">
        <input className="search-input" placeholder="Search" />
        <button className="search-btn" aria-label="Search">
          <svg viewBox="0 0 24 24" aria-hidden="true" className="search-icon">
            <path
              d="M15.5 14h-.79l-.28-.27A6.5 6.5 0 1 0 14 15.5l.27.28v.79L20 22l2-2-6.5-6zM10 15a5 5 0 1 1 0-10 5 5 0 0 1 0 10z"
              fill="currentColor"
            />
          </svg>
        </button>
        <button className="mic-btn" aria-label="Voice search">
          <svg viewBox="0 0 24 24" aria-hidden="true" className="mic-icon">
            <path
              d="M12 14a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3zm5-3a1 1 0 1 1 2 0 7 7 0 0 1-6 6.92V21h3a1 1 0 1 1 0 2H8a1 1 0 1 1 0-2h3v-3.08A7 7 0 0 1 5 11a1 1 0 1 1 2 0 5 5 0 1 0 10 0z"
              fill="currentColor"
            />
          </svg>
        </button>
      </div>

      <div className="header-right">
        <Link to="/upload" className="upload-link">
          <svg viewBox="0 0 24 24" aria-hidden="true" className="create-icon">
            <path d="M19 11h-6V5h-2v6H5v2h6v6h2v-6h6z" fill="currentColor" />
          </svg>
          <span>Create</span>
        </Link>
        <button className="icon-btn bell-btn" aria-label="Notifications">
          <svg viewBox="0 0 24 24" aria-hidden="true" className="bell-icon">
            <path
              d="M12 22a2.5 2.5 0 0 0 2.45-2h-4.9A2.5 2.5 0 0 0 12 22zm7-4v-1l-1-1v-4a6 6 0 1 0-12 0v4l-1 1v1h14z"
              fill="currentColor"
            />
          </svg>
        </button>
        <div className="avatar">YC</div>
      </div>
    </header>
  );
}
