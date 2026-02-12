import { Link } from 'react-router-dom';

import type { Video } from '../types';

type VideoCardProps = {
  video: Video;
};

export function VideoCard({ video }: VideoCardProps) {
  return (
    <Link to={`/watch/${video.id}`} className="video-card">
      <div className="thumbnail-placeholder">Video #{video.id}</div>
      <h3>{video.title}</h3>
      <p>{video.description || 'No description'}</p>
      <small>{video.views} views</small>
    </Link>
  );
}
