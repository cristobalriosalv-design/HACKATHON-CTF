import { FormEvent, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { addComment, fetchComments, fetchRecommended, fetchVideo, toAbsoluteApiUrl, toAbsoluteStreamUrl } from '../api/client';
import { useVideoCache } from '../context/VideoCacheContext';

function formatViews(views: number): string {
  return `${views.toLocaleString()} views`;
}

export function WatchPage() {
  const { id } = useParams();
  const videoId = Number(id);
  const queryClient = useQueryClient();
  const { streamCache } = useVideoCache();
  const [author, setAuthor] = useState('');
  const [content, setContent] = useState('');

  const videoQuery = useQuery({
    queryKey: ['video', videoId],
    queryFn: () => fetchVideo(videoId),
    enabled: Number.isFinite(videoId),
  });

  const commentsQuery = useQuery({
    queryKey: ['comments', videoId],
    queryFn: () => fetchComments(videoId),
    enabled: Number.isFinite(videoId),
  });

  const recommendedQuery = useQuery({
    queryKey: ['recommended', videoId],
    queryFn: () => fetchRecommended(videoId),
    enabled: Number.isFinite(videoId),
  });

  const commentMutation = useMutation({
    mutationFn: () => addComment(videoId, author, content),
    onSuccess: async () => {
      setAuthor('');
      setContent('');
      await queryClient.invalidateQueries({ queryKey: ['comments', videoId] });
    },
  });

  const streamSrc = useMemo(() => {
    if (!videoQuery.data) return '';
    return streamCache[videoId] ?? toAbsoluteStreamUrl(videoQuery.data.stream_url);
  }, [streamCache, videoId, videoQuery.data]);

  if (videoQuery.isLoading) return <p className="status-text">Loading video...</p>;
  if (!videoQuery.data) return <p className="status-text">Video not found.</p>;

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!author.trim() || !content.trim()) return;
    await commentMutation.mutateAsync();
  };

  return (
    <main className="watch-layout">
      <section>
        <video src={streamSrc} controls className="player" />
        <h1 className="watch-title">{videoQuery.data.title}</h1>
        <p className="watch-stats">{formatViews(videoQuery.data.views)}</p>
        <p className="watch-description">{videoQuery.data.description || 'No description'}</p>

        <div className="comments">
          <h2>Comments</h2>
          <form onSubmit={handleSubmit} className="comment-form">
            <input
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              placeholder="Your name"
              required
            />
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Add a comment"
              required
            />
            <button type="submit" disabled={commentMutation.isPending}>
              {commentMutation.isPending ? 'Posting...' : 'Post'}
            </button>
          </form>

          {commentsQuery.data?.map((comment) => (
            <article key={comment.id} className="comment-item">
              <strong>{comment.author}</strong>
              <p>{comment.content}</p>
            </article>
          ))}
        </div>
      </section>

      <aside>
        <h2 className="rec-title">Recommended</h2>
        <div className="recommended-list">
          {recommendedQuery.data?.map((video) => (
            <Link key={video.id} to={`/watch/${video.id}`} className="recommended-item">
              <div className="recommended-thumb">
                {video.thumbnail_url ? <img src={toAbsoluteApiUrl(video.thumbnail_url)} alt={`${video.title} thumbnail`} /> : null}
              </div>
              <div>
                <strong>{video.title}</strong>
                <span>{formatViews(video.views)}</span>
              </div>
            </Link>
          ))}
        </div>
      </aside>
    </main>
  );
}
