import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="h-screen w-full bg-[#050505] text-white flex flex-col items-center justify-center p-6">
          <div className="max-w-md w-full glass-panel rounded-3xl p-8 border border-red-500/20 flex flex-col items-center text-center relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-red-500 to-transparent"></div>
            <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mb-6 border border-red-500/20">
              <AlertTriangle className="w-8 h-8 text-red-400" />
            </div>
            <h1 className="text-2xl font-light tracking-widest text-red-400 mb-4 uppercase">System Error</h1>
            <p className="text-neutral-400 font-mono text-sm mb-8 leading-relaxed">
              A critical UI exception occurred. The neural mesh interface has halted to prevent cascading failures.
            </p>
            <p className="text-xs text-neutral-600 font-mono bg-black/50 p-4 rounded-xl w-full text-left overflow-hidden text-ellipsis whitespace-nowrap mb-8 border border-white/5">
              {this.state.error?.message}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="flex items-center gap-2 px-6 py-3 rounded-full bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30 transition-all uppercase tracking-widest text-xs font-bold"
            >
              <RefreshCw className="w-4 h-4" />
              Reinitialize Subsystem
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
