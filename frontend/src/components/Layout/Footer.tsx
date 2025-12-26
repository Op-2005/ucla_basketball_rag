import { Cpu, Sparkles } from 'lucide-react';

export function Footer() {
  return (
    <footer className="gradient-dark text-primary-foreground py-4 border-t border-ucla-gold/20">
      <div className="container mx-auto px-4">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-2 text-sm">
          <p className="text-primary-foreground/80">
            © 2025 UCLA Women's Basketball Analytics
          </p>
          <div className="flex items-center gap-2 text-ucla-gold">
            <Sparkles className="w-4 h-4" />
            <span>Powered by</span>
            <Cpu className="w-4 h-4" />
            <span className="font-medium">Claude AI & Advanced RAG Technology</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
