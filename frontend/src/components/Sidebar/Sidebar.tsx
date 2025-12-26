import { StatsCard } from './StatsCard';
import { QuickActions } from './QuickActions';
import { RecentQueries } from './RecentQueries';

export function Sidebar() {
  return (
    <aside className="w-full lg:w-80 flex-shrink-0 p-4 space-y-4 overflow-y-auto scrollbar-thin">
      <StatsCard />
      <QuickActions />
      <RecentQueries />
    </aside>
  );
}
