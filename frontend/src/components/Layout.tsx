import React from 'react';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="flex h-screen w-full bg-[#050505] text-white overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-6 relative">
        {/* Glow effect background */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none -z-10">
          <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-600/20 rounded-full blur-[120px]"></div>
          <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-purple-600/20 rounded-full blur-[120px]"></div>
        </div>
        <div className="h-full w-full glass-panel rounded-3xl p-6 relative overflow-hidden shadow-[0_0_40px_rgba(0,0,0,0.5)]">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
