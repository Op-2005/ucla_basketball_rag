import { CheckCircle, MessageSquare } from 'lucide-react';

const features = [
  'Player statistics and performance',
  'Game analysis and results',
  'Team comparisons and trends',
  'Season highlights and records',
];

export function WelcomeMessage() {
  return (
    <div className="gradient-gold rounded-xl p-6 mb-6 shadow-lg animate-scale-in">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-full gradient-primary flex items-center justify-center flex-shrink-0 shadow-md">
          <span className="text-2xl">🏀</span>
        </div>
        <div className="flex-1">
          <h2 className="font-display font-bold text-xl text-secondary-foreground mb-2">
            Welcome to UCLA Women's Basketball Analytics!
          </h2>
          <p className="text-secondary-foreground/80 mb-4">
            I'm your AI-powered basketball assistant. Ask me anything about:
          </p>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-4">
            {features.map((feature) => (
              <div key={feature} className="flex items-center gap-2 text-secondary-foreground/90">
                <CheckCircle className="w-4 h-4 text-ucla-blue flex-shrink-0" />
                <span className="text-sm">{feature}</span>
              </div>
            ))}
          </div>

          <div className="bg-secondary-foreground/10 rounded-lg p-3 mt-4">
            <div className="flex items-center gap-2 text-secondary-foreground mb-1">
              <MessageSquare className="w-4 h-4" />
              <span className="font-medium text-sm">Try asking:</span>
            </div>
            <p className="text-sm text-secondary-foreground/80 italic">
              "Who scored the most points against USC?" or "Compare Rice and Jones' assist numbers"
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
