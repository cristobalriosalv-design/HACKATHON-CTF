import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

import { fetchVideos, toAbsoluteStreamUrl } from '../api/client';
import type { Video } from '../types';

type VideoCacheContextValue = {
  videos: Video[];
  streamCache: Record<number, string>;
  loading: boolean;
  refreshVideos: () => Promise<void>;
};

const VideoCacheContext = createContext<VideoCacheContextValue | undefined>(undefined);

export function VideoCacheProvider({ children }: { children: React.ReactNode }) {
  const [videos, setVideos] = useState<Video[]>([]);
  const [streamCache, setStreamCache] = useState<Record<number, string>>({});
  const [loading, setLoading] = useState(true);

  const loadAll = useCallback(async () => {
    setLoading(true);
    const allVideos = await fetchVideos();
    setVideos(allVideos);

    const cacheEntries = await Promise.all(
      allVideos.map(async (video) => {
        const response = await fetch(toAbsoluteStreamUrl(video.stream_url));
        const blob = await response.blob();
        const objectUrl = URL.createObjectURL(blob);
        return [video.id, objectUrl] as const;
      })
    );

    setStreamCache(Object.fromEntries(cacheEntries));
    setLoading(false);
  }, []);

  useEffect(() => {
    void loadAll();
    return () => {
      Object.values(streamCache).forEach((url) => URL.revokeObjectURL(url));
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const value = useMemo(
    () => ({ videos, streamCache, loading, refreshVideos: loadAll }),
    [videos, streamCache, loading, loadAll]
  );

  return <VideoCacheContext.Provider value={value}>{children}</VideoCacheContext.Provider>;
}

export function useVideoCache() {
  const context = useContext(VideoCacheContext);
  if (!context) {
    throw new Error('useVideoCache must be used within VideoCacheProvider');
  }
  return context;
}
