import { Star, Target, Percent, Trophy, Users, Award } from 'lucide-react';
import { useApp } from '@/context/AppContext';

const quickActions = [
  {
    icon: Star,
    label: 'Leading Scorer',
    query: "Who is the team's leading scorer this season?",
  },
  {
    icon: Target,
    label: 'Betts Stats',
    query: "What are Lauren Betts' season statistics?",
  },
  {
    icon: Percent,
    label: 'Shooting %',
    query: "Show me the team's shooting percentages",
  },
  {
    icon: Trophy,
    label: 'Top Rebounders',
    query: 'Who are the top 3 rebounders on the team?',
  },
  {
    icon: Users,
    label: 'Assist Leaders',
    query: 'Show me assist leaders and their averages',
  },
  {
    icon: Award,
    label: 'Best Game',
    query: 'What was our highest scoring game this season?',
  },
];

export function QuickActions() {
  const { sendMessage, isLoading } = useApp();

  const handleClick = (query: string) => {
    if (!isLoading) {
      sendMessage(query);
    }
  };

  return (
    <div className="bg-card rounded-xl border border-border p-4 shadow-sm">
      <h3 className="font-display font-semibold text-sm text-card-foreground mb-4">
        Quick Actions
      </h3>
      <div className="grid grid-cols-2 gap-2">
        {quickActions.map((action) => (
          <button
            key={action.label}
            onClick={() => handleClick(action.query)}
            disabled={isLoading}
            className="flex flex-col items-center gap-2 p-3 rounded-lg bg-muted hover:bg-ucla-gold/20 hover:text-ucla-blue transition-all duration-200 group disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div className="w-10 h-10 rounded-full bg-ucla-blue/10 group-hover:bg-ucla-blue/20 flex items-center justify-center transition-colors">
              <action.icon className="w-5 h-5 text-ucla-blue" />
            </div>
            <span className="text-xs font-medium text-center leading-tight">
              {action.label}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
