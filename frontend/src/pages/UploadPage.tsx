import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { uploadVideo } from '../api/client';
import { useVideoCache } from '../context/VideoCacheContext';

export function UploadPage() {
  const navigate = useNavigate();
  const { refreshVideos } = useVideoCache();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!file || !title.trim()) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('file', file);

    try {
      const uploaded = await uploadVideo(formData);
      setLoading(false);
      navigate(`/watch/${uploaded.id}`);
      void refreshVideos();
    } catch {
      setError('Upload failed. Please try again.');
      setLoading(false);
    }
  };

  return (
    <main className="upload-main">
      <section className="upload-panel">
        <h1>Upload video</h1>
        <p>Add details and publish your content.</p>

        <form onSubmit={handleSubmit} className="upload-form">
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title" required />
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Description" />
          <input
            type="file"
            accept="video/*"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Uploading...' : 'Upload'}
          </button>
        </form>

        {error ? <p className="error-text">{error}</p> : null}
      </section>
    </main>
  );
}
