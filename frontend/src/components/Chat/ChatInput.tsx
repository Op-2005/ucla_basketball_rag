import { useState, KeyboardEvent } from 'react';
import { Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useApp } from '@/context/AppContext';
import { cn } from '@/lib/utils';

const suggestions = [
  'Leading scorer',
  'Team stats',
  'Recent games',
  'Player comparison',
];

export function ChatInput() {
  const [input, setInput] = useState('');
  const { sendMessage, isLoading } = useApp();

  const handleSubmit = async () => {
    if (!input.trim() || isLoading) return;
    
    const query = input.trim();
    setInput('');
    await sendMessage(query);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
  };

  return (
    <div className="border-t border-border bg-card p-4">
      {/* Suggestion chips */}
      <div className="flex flex-wrap gap-2 mb-3">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => handleSuggestionClick(suggestion)}
            className="px-3 py-1.5 text-xs font-medium rounded-full bg-muted hover:bg-ucla-gold/20 hover:text-ucla-blue transition-colors"
          >
            {suggestion}
          </button>
        ))}
      </div>

      {/* Input area */}
      <div className="flex items-center gap-3">
        <div className="flex-1 relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about UCLA women's basketball..."
            disabled={isLoading}
            className={cn(
              "w-full px-4 py-3 rounded-xl border border-border bg-background",
              "focus:outline-none focus:ring-2 focus:ring-ucla-gold focus:border-transparent",
              "placeholder:text-muted-foreground text-sm",
              "transition-all duration-200",
              isLoading && "opacity-50 cursor-not-allowed"
            )}
            autoFocus
          />
        </div>
        <Button
          onClick={handleSubmit}
          disabled={!input.trim() || isLoading}
          className={cn(
            "w-12 h-12 rounded-full gradient-primary hover:opacity-90",
            "flex items-center justify-center",
            "transition-all duration-200",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            !isLoading && input.trim() && "animate-pulse-glow"
          )}
        >
          <Send className="w-5 h-5" />
        </Button>
      </div>
    </div>
  );
}
