import { Calendar, Cpu } from 'lucide-react';
import { useApp } from '@/context/AppContext';

export function StatsCard() {
  const { stats } = useApp();

  const statItems = [
    {
      icon: Calendar,
      label: 'Games Analyzed',
      value: stats.gamesCount,
      gradient: 'gradient-primary',
    },
    {
      icon: Cpu,
      label: 'AI Tokens',
      value: stats.totalTokens.toLocaleString(),
      gradient: 'gradient-dark',
    },
  ];

  return (
    <div className="bg-card rounded-xl border border-border p-4 shadow-sm">
      <h3 className="font-display font-semibold text-sm text-card-foreground mb-4">
        Quick Stats
      </h3>
      <div className="space-y-3">
        {statItems.map((item) => (
          <div
            key={item.label}
            className={`${item.gradient} rounded-lg p-3 text-primary-foreground`}
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary-foreground/20 flex items-center justify-center">
                <item.icon className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs text-primary-foreground/80">{item.label}</p>
                <p className="font-display font-bold text-lg">{item.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
