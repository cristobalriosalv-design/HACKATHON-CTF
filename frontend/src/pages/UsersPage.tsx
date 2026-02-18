import { FormEvent, useState } from 'react';

import { toAbsoluteApiUrl } from '../api/client';
import { useUserContext } from '../context/UserContext';

export function UsersPage() {
  const {
    users,
    providers,
    currentUserId,
    setCurrentUserId,
    createNewUser,
    isSubscribedTo,
    subscribe,
    unsubscribe,
  } = useUserContext();

  const [displayName, setDisplayName] = useState('');
  const [provider, setProvider] = useState('local');
  const [providerSubject, setProviderSubject] = useState('');
  const [email, setEmail] = useState('');
  const [avatar, setAvatar] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!displayName.trim()) return;

    setSaving(true);
    setError(null);
    try {
      await createNewUser({
        displayName: displayName.trim(),
        provider,
        providerSubject,
        email,
        avatar,
      });
      setDisplayName('');
      setProviderSubject('');
      setEmail('');
      setAvatar(null);
    } catch {
      setError('Could not create user. Check provider subject uniqueness and input values.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <main className="users-main">
      <section className="upload-panel">
        <h1>Create user</h1>
        <form onSubmit={handleSubmit} className="upload-form">
          <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder="Display name" required />

          <select value={provider} onChange={(e) => setProvider(e.target.value)}>
            {providers.map((providerName) => (
              <option key={providerName} value={providerName}>
                {providerName}
              </option>
            ))}
          </select>

          <input
            value={providerSubject}
            onChange={(e) => setProviderSubject(e.target.value)}
            placeholder="Provider subject (optional for local)"
          />

          <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email (optional)" type="email" />

          <input type="file" accept="image/*" onChange={(e) => setAvatar(e.target.files?.[0] ?? null)} />

          <button type="submit" disabled={saving}>
            {saving ? 'Creating...' : 'Create user'}
          </button>
        </form>
        {error ? <p className="error-text">{error}</p> : null}
      </section>

      <section className="upload-panel">
        <h2>Users</h2>
        <div className="user-list">
          {users.map((user) => {
            const avatarUrl = user.avatar_url ? toAbsoluteApiUrl(user.avatar_url) : null;
            const subscribed = isSubscribedTo(user.id);
            const canSubscribe = currentUserId !== null && currentUserId !== user.id;

            return (
              <article key={user.id} className="user-row">
                <div className="user-row-left">
                  {avatarUrl ? (
                    <img className="avatar avatar-image" src={avatarUrl} alt={`${user.display_name} avatar`} />
                  ) : (
                    <div className="avatar">{user.display_name.slice(0, 2).toUpperCase()}</div>
                  )}
                  <div>
                    <strong>{user.display_name}</strong>
                    <p>User #{user.id}</p>
                  </div>
                </div>
                <div className="user-row-actions">
                  <button type="button" className="secondary-btn" onClick={() => setCurrentUserId(user.id)}>
                    Use as current
                  </button>
                  {canSubscribe ? (
                    subscribed ? (
                      <button type="button" onClick={() => void unsubscribe(user.id)}>
                        Unsubscribe
                      </button>
                    ) : (
                      <button type="button" onClick={() => void subscribe(user.id)}>
                        Subscribe
                      </button>
                    )
                  ) : null}
                </div>
              </article>
            );
          })}
        </div>
      </section>
    </main>
  );
}
