import { Link } from 'react-router-dom';

import { toAbsoluteApiUrl } from '../api/client';
import { useUserContext } from '../context/UserContext';

export function Header() {
  const { users, currentUserId, setCurrentUserId, currentUser } = useUserContext();
  const avatarSrc = currentUser?.avatar_url ? toAbsoluteApiUrl(currentUser.avatar_url) : null;

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
          <span className="brand-text">EIATube</span>
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
        <label className="user-selector-wrap" htmlFor="current-user-select">
          <span className="user-selector-label">Current user</span>
          <select
            id="current-user-select"
            className="user-selector"
            value={currentUserId ?? ''}
            onChange={(event) => {
              const next = Number(event.target.value);
              setCurrentUserId(Number.isFinite(next) && next > 0 ? next : null);
            }}
          >
            <option value="">None</option>
            {users.map((user) => (
              <option key={user.id} value={user.id}>
                {user.display_name}
              </option>
            ))}
          </select>
        </label>

        <Link to="/upload" className="upload-link">
          <svg viewBox="0 0 24 24" aria-hidden="true" className="create-icon">
            <path d="M19 11h-6V5h-2v6H5v2h6v6h2v-6h6z" fill="currentColor" />
          </svg>
          <span>Create</span>
        </Link>

        <Link to="/users" className="upload-link">
          <span>Manage Users</span>
        </Link>

        {avatarSrc ? (
          <img className="avatar avatar-image" src={avatarSrc} alt={`${currentUser?.display_name ?? 'Current user'} avatar`} />
        ) : (
          <div className="avatar">{currentUser?.display_name.slice(0, 2).toUpperCase() ?? 'EI'}</div>
        )}
      </div>
    </header>
  );
}
