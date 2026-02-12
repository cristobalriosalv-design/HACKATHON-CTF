import { useVideoCache } from '../context/VideoCacheContext';
import { VideoCard } from '../components/VideoCard';

export function HomePage() {
  const { videos, loading } = useVideoCache();

  if (loading) {
    return <p className="status-text">Loading videos...</p>;
  }

  return (
    <main className="home-main">
      <div className="chip-row">
        <button className="chip chip-active">All</button>
        <button className="chip">Music</button>
        <button className="chip">Gaming</button>
        <button className="chip">News</button>
        <button className="chip">Live</button>
      </div>

      <div className="grid">
        {videos.map((video) => (
          <VideoCard key={video.id} video={video} />
        ))}
      </div>
    </main>
  );
}
