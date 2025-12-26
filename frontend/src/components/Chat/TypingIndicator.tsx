import { Bot } from 'lucide-react';

export function TypingIndicator() {
  return (
    <div className="flex justify-start mb-4 animate-fade-in">
      <div className="flex items-start gap-2">
        <div className="w-8 h-8 rounded-full gradient-gold flex items-center justify-center flex-shrink-0">
          <Bot className="w-4 h-4 text-secondary-foreground" />
        </div>
        <div className="bg-card border border-border rounded-2xl rounded-tl-md px-4 py-3 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-ucla-blue animate-bounce-dot" />
              <span className="w-2 h-2 rounded-full bg-ucla-blue animate-bounce-dot-delay-1" />
              <span className="w-2 h-2 rounded-full bg-ucla-blue animate-bounce-dot-delay-2" />
            </div>
            <span className="text-sm text-muted-foreground">AI is analyzing your query...</span>
          </div>
        </div>
      </div>
    </div>
  );
}
