export type Video = {
  id: number;
  title: string;
  description: string;
  created_at: string;
  views: number;
  stream_url: string;
  thumbnail_url: string | null;
};

export type Comment = {
  id: number;
  video_id: number;
  author: string;
  content: string;
  created_at: string;
};
