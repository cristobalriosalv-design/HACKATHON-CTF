import { useMemo, useState } from 'react';

import { useVideoCache } from '../context/VideoCacheContext';
import { VideoCard } from '../components/VideoCard';

export function HomePage() {
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'music' | 'gaming' | 'news'>('all');
  const { videos, loading } = useVideoCache();
  const filteredVideos = useMemo(() => {
    if (selectedCategory === 'all') return videos;
    return videos.filter((video) => (video.category ?? '').toLowerCase() === selectedCategory);
  }, [selectedCategory, videos]);

  if (loading) {
    return <p className="status-text">Loading videos...</p>;
  }

  return (
    <main className="home-main">
      <div className="chip-row">
        <button
          type="button"
          className={selectedCategory === 'all' ? 'chip chip-active' : 'chip'}
          onClick={() => setSelectedCategory('all')}
        >
          All
        </button>
        <button
          type="button"
          className={selectedCategory === 'music' ? 'chip chip-active' : 'chip'}
          onClick={() => setSelectedCategory('music')}
        >
          Music
        </button>
        <button
          type="button"
          className={selectedCategory === 'gaming' ? 'chip chip-active' : 'chip'}
          onClick={() => setSelectedCategory('gaming')}
        >
          Gaming
        </button>
        <button
          type="button"
          className={selectedCategory === 'news' ? 'chip chip-active' : 'chip'}
          onClick={() => setSelectedCategory('news')}
        >
          News
        </button>
      </div>

      <div className="grid">
        {filteredVideos.map((video) => (
          <VideoCard key={video.id} video={video} />
        ))}
      </div>
    </main>
  );
}
