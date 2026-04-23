import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

import { fetchVideos } from '../api/client';
import type { Video } from '../types';

type VideoCacheContextValue = {
  videos: Video[];
  loading: boolean;
  refreshVideos: () => Promise<void>;
};

const VideoCacheContext = createContext<VideoCacheContextValue | undefined>(undefined);

export function VideoCacheProvider({ children }: { children: React.ReactNode }) {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);

  const loadAll = useCallback(async () => {
    setLoading(true);

    try {
      const allVideos = await fetchVideos();
      setVideos(allVideos);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadAll();
  }, [loadAll]);

  const value = useMemo(() => ({ videos, loading, refreshVideos: loadAll }), [videos, loading, loadAll]);

  return <VideoCacheContext.Provider value={value}>{children}</VideoCacheContext.Provider>;
}

export function useVideoCache() {
  const context = useContext(VideoCacheContext);
  if (!context) {
    throw new Error('useVideoCache must be used within VideoCacheProvider');
  }
  return context;
}
