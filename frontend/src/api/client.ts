import type { Comment, Video } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export const toAbsoluteStreamUrl = (streamUrl: string) => `${API_BASE_URL}${streamUrl}`;

export async function fetchVideos(): Promise<Video[]> {
  const response = await fetch(`${API_BASE_URL}/videos`);
  if (!response.ok) throw new Error('Failed to fetch videos');
  return response.json();
}

export async function fetchVideo(videoId: number): Promise<Video> {
  const response = await fetch(`${API_BASE_URL}/videos/${videoId}`);
  if (!response.ok) throw new Error('Failed to fetch video');
  return response.json();
}

export async function uploadVideo(formData: FormData): Promise<Video> {
  const response = await fetch(`${API_BASE_URL}/videos/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) throw new Error('Failed to upload video');
  return response.json();
}

export async function fetchComments(videoId: number): Promise<Comment[]> {
  const response = await fetch(`${API_BASE_URL}/videos/${videoId}/comments`);
  if (!response.ok) throw new Error('Failed to fetch comments');
  return response.json();
}

export async function addComment(videoId: number, author: string, content: string): Promise<Comment> {
  const response = await fetch(`${API_BASE_URL}/videos/${videoId}/comments`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ author, content }),
  });
  if (!response.ok) throw new Error('Failed to post comment');
  return response.json();
}

export async function fetchRecommended(videoId: number): Promise<Video[]> {
  const response = await fetch(`${API_BASE_URL}/videos/${videoId}/recommended`);
  if (!response.ok) throw new Error('Failed to fetch recommended videos');
  return response.json();
}
