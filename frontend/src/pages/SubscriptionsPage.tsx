import { useQuery } from '@tanstack/react-query';

import { fetchSubscriptionFeed } from '../api/client';
import { VideoCard } from '../components/VideoCard';
import { useUserContext } from '../context/UserContext';

export function SubscriptionsPage() {
  const { currentUser } = useUserContext();

  const feedQuery = useQuery({
    queryKey: ['subscription-feed', currentUser?.id],
    queryFn: () => fetchSubscriptionFeed(currentUser!.id),
    enabled: !!currentUser,
  });

  if (!currentUser) {
    return <p className="status-text">Choose a current user to see subscription videos.</p>;
  }

  if (feedQuery.isLoading) {
    return <p className="status-text">Loading subscriptions feed...</p>;
  }

  if (!feedQuery.data || feedQuery.data.length === 0) {
    return <p className="status-text">No subscription videos yet. Subscribe to creators and upload videos.</p>;
  }

  return (
    <main className="home-main">
      <h1 className="page-title">Subscription feed</h1>
      <div className="grid">
        {feedQuery.data.map((video) => (
          <VideoCard key={video.id} video={video} />
        ))}
      </div>
    </main>
  );
}
