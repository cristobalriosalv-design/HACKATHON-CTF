import { useVideoCache } from '../context/VideoCacheContext';
import { VideoCard } from '../components/VideoCard';

export function HomePage() {
  const { videos, loading } = useVideoCache();

  if (loading) {
    return <p>Loading videos...</p>;
  }

  return (
    <main>
      <h1>All Videos</h1>
      <div className="grid">
        {videos.map((video) => (
          <VideoCard key={video.id} video={video} />
        ))}
      </div>
    </main>
  );
}
