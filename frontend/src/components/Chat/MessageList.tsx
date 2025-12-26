import { useEffect, useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import { TypingIndicator } from './TypingIndicator';
import { WelcomeMessage } from './WelcomeMessage';
import { useApp } from '@/context/AppContext';

export function MessageList() {
  const { messages, isLoading } = useApp();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto p-4 scrollbar-thin">
      {messages.length === 0 && <WelcomeMessage />}
      
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      
      {isLoading && <TypingIndicator />}
      
      <div ref={bottomRef} />
    </div>
  );
}
