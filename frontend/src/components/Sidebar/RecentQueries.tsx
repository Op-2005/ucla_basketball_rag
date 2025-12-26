import { Clock, MessageSquare } from 'lucide-react';
import { useApp } from '@/context/AppContext';

export function RecentQueries() {
  const { history, sendMessage, isLoading } = useApp();

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  const truncate = (text: string, maxLength: number = 50) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const handleClick = (query: string) => {
    if (!isLoading) {
      sendMessage(query);
    }
  };

  const recentItems = history.slice(-8).reverse();

  return (
    <div className="bg-card rounded-xl border border-border p-4 shadow-sm">
      <h3 className="font-display font-semibold text-sm text-card-foreground mb-4 flex items-center gap-2">
        <Clock className="w-4 h-4 text-muted-foreground" />
        Recent Queries
      </h3>
      
      {recentItems.length === 0 ? (
        <div className="text-center py-6">
          <MessageSquare className="w-8 h-8 text-muted-foreground/50 mx-auto mb-2" />
          <p className="text-sm text-muted-foreground">No chat history yet</p>
          <p className="text-xs text-muted-foreground/70 mt-1">
            Start a conversation to see your history
          </p>
        </div>
      ) : (
        <div className="space-y-2 max-h-64 overflow-y-auto scrollbar-thin">
          {recentItems.map((item, index) => (
            <button
              key={index}
              onClick={() => handleClick(item.query)}
              disabled={isLoading}
              className="w-full text-left p-2.5 rounded-lg bg-muted/50 hover:bg-ucla-gold/10 transition-colors group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <p className="text-sm text-card-foreground font-medium group-hover:text-ucla-blue transition-colors">
                {truncate(item.query)}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {formatTime(item.timestamp)}
              </p>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
