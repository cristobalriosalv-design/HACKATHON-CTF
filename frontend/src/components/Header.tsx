import { Link } from 'react-router-dom';

export function Header() {
  return (
    <header className="header">
      <Link to="/" className="brand">
        YT Clone
      </Link>
      <nav>
        <Link to="/upload" className="nav-link">
          Upload
        </Link>
      </nav>
    </header>
  );
}
