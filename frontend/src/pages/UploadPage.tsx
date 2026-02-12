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

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!file || !title.trim()) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('file', file);

    const uploaded = await uploadVideo(formData);
    await refreshVideos();
    setLoading(false);
    navigate(`/watch/${uploaded.id}`);
  };

  return (
    <main>
      <h1>Upload Video</h1>
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
    </main>
  );
}
