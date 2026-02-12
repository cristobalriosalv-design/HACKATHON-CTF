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
          <span className="brand-badge">▶</span>
          <span className="brand-text">YouTube</span>
        </Link>
      </div>

      <div className="search-wrap">
        <input className="search-input" placeholder="Search" />
        <button className="search-btn" aria-label="Search">
          Search
        </button>
      </div>

      <div className="header-right">
        <Link to="/upload" className="upload-link">
          Create
        </Link>
        <div className="avatar">YC</div>
      </div>
    </header>
  );
}
