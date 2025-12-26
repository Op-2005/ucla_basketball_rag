import { Bot, User, AlertCircle, Info } from 'lucide-react';
import type { Message } from '@/types';
import { cn } from '@/lib/utils';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const { type, content, timestamp, tokens } = message;

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  const renderContent = (text: string) => {
    // Simple markdown-like rendering
    return text.split('\n').map((line, i) => {
      // Bold text
      let processed = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      // Italic text
      processed = processed.replace(/\*(.*?)\*/g, '<em>$1</em>');
      
      return (
        <span key={i}>
          <span dangerouslySetInnerHTML={{ __html: processed }} />
          {i < text.split('\n').length - 1 && <br />}
        </span>
      );
    });
  };

  if (type === 'user') {
    return (
      <div className="flex justify-end mb-4 animate-slide-in-up">
        <div className="max-w-[80%] md:max-w-[70%]">
          <div className="gradient-primary text-primary-foreground rounded-2xl rounded-tr-md px-4 py-3 shadow-md">
            <p className="text-sm leading-relaxed">{content}</p>
          </div>
          <div className="flex justify-end items-center gap-2 mt-1 px-2">
            <span className="text-xs text-muted-foreground">{formatTime(timestamp)}</span>
            <div className="w-6 h-6 rounded-full bg-ucla-blue flex items-center justify-center">
              <User className="w-3.5 h-3.5 text-primary-foreground" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (type === 'assistant') {
    return (
      <div className="flex justify-start mb-4 animate-slide-in-up">
        <div className="max-w-[80%] md:max-w-[70%]">
          <div className="bg-card border border-border rounded-2xl rounded-tl-md px-4 py-3 shadow-sm">
            <p className="text-sm leading-relaxed text-card-foreground">
              {renderContent(content)}
            </p>
          </div>
          <div className="flex items-center gap-2 mt-1 px-2">
            <div className="w-6 h-6 rounded-full gradient-gold flex items-center justify-center">
              <Bot className="w-3.5 h-3.5 text-secondary-foreground" />
            </div>
            <span className="text-xs text-muted-foreground">{formatTime(timestamp)}</span>
            {tokens && (
              <span className="text-xs text-muted-foreground">• {tokens} tokens</span>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (type === 'system') {
    return (
      <div className="flex justify-center mb-4 animate-slide-in-up">
        <div className="bg-ucla-gold/20 border border-ucla-gold/30 rounded-xl px-4 py-2 max-w-[90%]">
          <div className="flex items-center gap-2 text-secondary-foreground">
            <Info className="w-4 h-4 text-ucla-gold" />
            <p className="text-sm">{content}</p>
          </div>
        </div>
      </div>
    );
  }

  if (type === 'error') {
    return (
      <div className="flex justify-center mb-4 animate-slide-in-up">
        <div className="bg-destructive/10 border border-destructive/30 rounded-xl px-4 py-3 max-w-[90%]">
          <div className="flex items-center gap-2 text-destructive">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <p className="text-sm">{content}</p>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
