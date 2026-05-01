import type { Comment, User, Video } from '../types';

function resolveApiBaseUrl(): string {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL as string;
  }

  if (typeof window !== 'undefined') {
    return `${window.location.protocol}//${window.location.hostname}:8000`;
  }

  return 'http://localhost:8000';
}

const API_BASE_URL = resolveApiBaseUrl();

export const toAbsoluteApiUrl = (relativeUrl: string) => `${API_BASE_URL}${relativeUrl}`;
export const toAbsoluteStreamUrl = (streamUrl: string) => toAbsoluteApiUrl(streamUrl);

type PaginationParams = {
  limit?: number;
  offset?: number;
};

function buildPaginationQuery(params?: PaginationParams): string {
  if (!params || (params.limit === undefined && params.offset === undefined)) {
    return '';
  }

  const query = new URLSearchParams();
  if (params.limit !== undefined) query.set('limit', String(params.limit));
  if (params.offset !== undefined) query.set('offset', String(params.offset));
  return `?${query.toString()}`;
}

async function parseErrorMessage(response: Response, fallback: string): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: string };
    if (payload?.detail) return payload.detail;
  } catch {
    // Ignore JSON parse issues and use fallback message.
  }
  return fallback;
}

async function requestJson<T>(input: RequestInfo | URL, init: RequestInit | undefined, fallbackError: string): Promise<T> {
  const response = await fetch(input, init);
  if (!response.ok) {
    const message = await parseErrorMessage(response, fallbackError);
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

async function requestNoContent(input: RequestInfo | URL, init: RequestInit | undefined, fallbackError: string): Promise<void> {
  const response = await fetch(input, init);
  if (!response.ok) {
    const message = await parseErrorMessage(response, fallbackError);
    throw new Error(message);
  }
}

export async function fetchVideos(params?: PaginationParams): Promise<Video[]> {
  return requestJson<Video[]>(`${API_BASE_URL}/videos${buildPaginationQuery(params)}`, undefined, 'Failed to fetch videos');
}

export async function fetchSubscriptionFeed(userId: number, params?: PaginationParams): Promise<Video[]> {
  return requestJson<Video[]>(
    `${API_BASE_URL}/users/${userId}/feed${buildPaginationQuery(params)}`,
    undefined,
    'Failed to fetch subscriptions feed'
  );
}

export async function fetchVideo(videoId: number): Promise<Video> {
  return requestJson<Video>(`${API_BASE_URL}/videos/${videoId}`, undefined, 'Failed to fetch video');
}

export async function incrementVideoViews(videoId: number): Promise<Video> {
  return requestJson<Video>(`${API_BASE_URL}/videos/${videoId}/views`, { method: 'POST' }, 'Failed to increment video views');
}

export async function deleteVideo(videoId: number, requesterUserId: number): Promise<void> {
  return requestNoContent(
    `${API_BASE_URL}/videos/${videoId}?requester_user_id=${requesterUserId}`,
    { method: 'DELETE' },
    'Failed to delete video'
  );
}

export async function uploadVideo(formData: FormData): Promise<Video> {
  return requestJson<Video>(`${API_BASE_URL}/videos/upload`, { method: 'POST', body: formData }, 'Failed to upload video');
}

export async function fetchComments(videoId: number, params?: PaginationParams): Promise<Comment[]> {
  return requestJson<Comment[]>(
    `${API_BASE_URL}/videos/${videoId}/comments${buildPaginationQuery(params)}`,
    undefined,
    'Failed to fetch comments'
  );
}

export async function addComment(videoId: number, author: string, content: string): Promise<Comment> {
  return requestJson<Comment>(
    `${API_BASE_URL}/videos/${videoId}/comments`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ author, content }),
    },
    'Failed to post comment'
  );
}

export async function fetchRecommended(videoId: number): Promise<Video[]> {
  return requestJson<Video[]>(
    `${API_BASE_URL}/videos/${videoId}/recommended`,
    undefined,
    'Failed to fetch recommended videos'
  );
}

export async function fetchUsers(params?: PaginationParams): Promise<User[]> {
  return requestJson<User[]>(`${API_BASE_URL}/users${buildPaginationQuery(params)}`, undefined, 'Failed to fetch users');
}

export async function fetchProviders(): Promise<string[]> {
  const data = await requestJson<{ providers: string[] }>(`${API_BASE_URL}/users/providers`, undefined, 'Failed to fetch providers');
  return data.providers;
}

export async function createUser(formData: FormData): Promise<User> {
  return requestJson<User>(`${API_BASE_URL}/users`, { method: 'POST', body: formData }, 'Failed to create user');
}

export async function fetchSubscriptions(userId: number, params?: PaginationParams): Promise<number[]> {
  const data = await requestJson<{ creator_ids: number[] }>(
    `${API_BASE_URL}/users/${userId}/subscriptions${buildPaginationQuery(params)}`,
    undefined,
    'Failed to fetch subscriptions'
  );
  return data.creator_ids;
}

export async function subscribeToUser(userId: number, creatorId: number): Promise<void> {
  return requestNoContent(`${API_BASE_URL}/users/${userId}/subscriptions/${creatorId}`, { method: 'POST' }, 'Failed to subscribe');
}

export async function unsubscribeFromUser(userId: number, creatorId: number): Promise<void> {
  return requestNoContent(
    `${API_BASE_URL}/users/${userId}/subscriptions/${creatorId}`,
    { method: 'DELETE' },
    'Failed to unsubscribe'
  );
}
