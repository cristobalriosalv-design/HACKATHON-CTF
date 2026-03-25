import type { Comment, User, Video } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export const toAbsoluteApiUrl = (relativeUrl: string) => `${API_BASE_URL}${relativeUrl}`;
export const toAbsoluteStreamUrl = (streamUrl: string) => toAbsoluteApiUrl(streamUrl);

export async function fetchVideos(): Promise<Video[]> {
  const response = await fetch(`${API_BASE_URL}/videos`);
  if (!response.ok) throw new Error('Failed to fetch videos');
  return response.json();
}

export async function fetchSubscriptionFeed(userId: number): Promise<Video[]> {
  const response = await fetch(`${API_BASE_URL}/users/${userId}/feed`);
  if (!response.ok) throw new Error('Failed to fetch subscriptions feed');
  return response.json();
}

export async function fetchVideo(videoId: number): Promise<Video> {
  const response = await fetch(`${API_BASE_URL}/videos/${videoId}`);
  if (!response.ok) throw new Error('Failed to fetch video');
  return response.json();
}

export async function deleteVideo(videoId: number, requesterUserId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/videos/${videoId}?requester_user_id=${requesterUserId}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete video');
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

export async function fetchUsers(): Promise<User[]> {
  const response = await fetch(`${API_BASE_URL}/users`);
  if (!response.ok) throw new Error('Failed to fetch users');
  return response.json();
}

export async function fetchProviders(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/users/providers`);
  if (!response.ok) throw new Error('Failed to fetch providers');
  const data = (await response.json()) as { providers: string[] };
  return data.providers;
}

export async function createUser(formData: FormData): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/users`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) throw new Error('Failed to create user');
  return response.json();
}

export async function fetchSubscriptions(userId: number): Promise<number[]> {
  const response = await fetch(`${API_BASE_URL}/users/${userId}/subscriptions`);
  if (!response.ok) throw new Error('Failed to fetch subscriptions');
  const data = (await response.json()) as { creator_ids: number[] };
  return data.creator_ids;
}

export async function subscribeToUser(userId: number, creatorId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/users/${userId}/subscriptions/${creatorId}`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to subscribe');
}

export async function unsubscribeFromUser(userId: number, creatorId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/users/${userId}/subscriptions/${creatorId}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to unsubscribe');
}
