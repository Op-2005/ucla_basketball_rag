import { Navbar } from '@/components/Layout/Navbar';
import { Footer } from '@/components/Layout/Footer';
import { ChatContainer } from '@/components/Chat/ChatContainer';
import { Sidebar } from '@/components/Sidebar/Sidebar';
import { AppProvider } from '@/context/AppContext';

const Index = () => {
  return (
    <AppProvider>
      <div className="min-h-screen flex flex-col bg-background">
        <Navbar />
        
        <main className="flex-1 flex flex-col lg:flex-row container mx-auto max-w-7xl">
          {/* Sidebar - Hidden on mobile, visible on desktop */}
          <div className="hidden lg:block border-r border-border">
            <Sidebar />
          </div>
          
          {/* Main Chat Area */}
          <div className="flex-1 flex flex-col min-h-[calc(100vh-8rem)]">
            <ChatContainer />
          </div>
          
          {/* Mobile Sidebar - Shown at bottom on mobile */}
          <div className="lg:hidden border-t border-border bg-muted/30">
            <Sidebar />
          </div>
        </main>
        
        <Footer />
      </div>
    </AppProvider>
  );
};

export default Index;
