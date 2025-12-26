import { RotateCcw, Download, Wifi } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useApp } from '@/context/AppContext';

export function Navbar() {
  const { clearChat } = useApp();

  const handleExport = () => {
    // Export functionality placeholder
    console.log('Export data');
  };

  return (
    <nav className="gradient-primary text-primary-foreground shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Branding */}
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-lg bg-white/10 flex items-center justify-center shadow-glow overflow-hidden">
              <img 
                src="/images/ucla-wbb-logo.jpg" 
                alt="UCLA Women's Basketball" 
                className="w-full h-full object-cover"
              />
            </div>
            <div className="hidden sm:block">
              <h1 className="font-display font-bold text-lg leading-tight">
                UCLA Women's Basketball
              </h1>
              <p className="text-xs text-primary-foreground/80">
                AI Analytics Assistant
              </p>
            </div>
          </div>

          {/* Status Indicator */}
          <div className="hidden md:flex items-center gap-2 bg-primary-foreground/10 px-3 py-1.5 rounded-full">
            <Wifi className="w-4 h-4 text-green-400" />
            <span className="text-sm font-medium">Online & Ready</span>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={clearChat}
              className="text-primary-foreground hover:bg-primary-foreground/10"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Reset Chat</span>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleExport}
              className="text-primary-foreground hover:bg-primary-foreground/10"
            >
              <Download className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Export</span>
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}
