import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import { toAbsoluteApiUrl } from '../api/client';
import { useUserContext } from '../context/UserContext';

export function Header() {
  const { users, currentUserId, setCurrentUserId, currentUser } = useUserContext();
  const avatarSrc = currentUser?.avatar_url ? toAbsoluteApiUrl(currentUser.avatar_url) : null;
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => {
    const stored = localStorage.getItem('eiatube-theme');
    return stored === 'dark';
  });
  const [searchFocused, setSearchFocused] = useState(false);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
    localStorage.setItem('eiatube-theme', isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);

  return (
    <header className="header">
      <div className="header-left">
        <button className="icon-btn" aria-label="Menu">
          <span className="hamburger-line" />
          <span className="hamburger-line" />
          <span className="hamburger-line" />
        </button>
        <Link to="/" className="brand">
          <span className="brand-badge">
            <span className="brand-play" />
          </span>
          <span className="brand-text">EIATube</span>
        </Link>
      </div>

      <div className={`search-wrap${searchFocused ? ' search-focused' : ''}`}>
        <div className="search-field">
          <input
            className="search-input"
            placeholder="Search videos…"
            onFocus={() => setSearchFocused(true)}
            onBlur={() => setSearchFocused(false)}
          />
          <button className="search-btn" aria-label="Search">
            <svg viewBox="0 0 24 24" aria-hidden="true" className="search-icon">
              <path
                d="M15.5 14h-.79l-.28-.27A6.5 6.5 0 1 0 14 15.5l.27.28v.79L20 22l2-2-6.5-6zM10 15a5 5 0 1 1 0-10 5 5 0 0 1 0 10z"
                fill="currentColor"
              />
            </svg>
          </button>
        </div>
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
          <span className="user-selector-label">Viewing as</span>
          <select
            id="current-user-select"
            className="user-selector"
            value={currentUserId ?? ''}
            onChange={(event) => {
              const next = Number(event.target.value);
              setCurrentUserId(Number.isFinite(next) && next > 0 ? next : null);
            }}
          >
            <option value="">Guest</option>
            {users.map((user) => (
              <option key={user.id} value={user.id}>
                {user.display_name}
              </option>
            ))}
          </select>
        </label>

        <Link to="/upload" className="create-btn">
          <svg viewBox="0 0 24 24" aria-hidden="true" className="create-icon">
            <path d="M19 11h-6V5h-2v6H5v2h6v6h2v-6h6z" fill="currentColor" />
          </svg>
          <span>Create</span>
        </Link>

        <Link to="/users" className="nav-pill">
          Manage Users
        </Link>

        <button
          type="button"
          className="theme-toggle"
          onClick={() => setIsDarkMode((previous) => !previous)}
          aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {isDarkMode ? (
            <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
              <path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-12.37l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06c.39-.39.39-1.03 0-1.41s-1.03-.39-1.41 0zM7.05 18.36l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06c.39-.39.39-1.03 0-1.41s-1.03-.39-1.41 0z"/>
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
              <path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-2.98 0-5.4-2.42-5.4-5.4 0-1.81.89-3.42 2.26-4.4-.44-.06-.9-.1-1.36-.1z"/>
            </svg>
          )}
          <span>{isDarkMode ? 'Light' : 'Dark'}</span>
        </button>

        <div className="avatar-wrap">
          {avatarSrc ? (
            <img className="avatar avatar-image" src={avatarSrc} alt={`${currentUser?.display_name ?? 'Current user'} avatar`} />
          ) : (
            <div className="avatar">{currentUser?.display_name.slice(0, 2).toUpperCase() ?? 'EI'}</div>
          )}
          {currentUser && <span className="avatar-online" />}
        </div>
      </div>
    </header>
  );
}