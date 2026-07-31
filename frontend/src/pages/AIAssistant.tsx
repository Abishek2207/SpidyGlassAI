import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';
import { api } from '../App';

const AIAssistant: React.FC = () => {
  const [messages, setMessages] = useState<{role: string, text: string}[]>([
    { role: 'assistant', text: 'SpidyGlass AI initialized. How can I assist you with the neural interface today?' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sarvamError, setSarvamError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping, sarvamError]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    setMessages(prev => [...prev, { role: 'user', text: input }]);
    setInput('');
    setIsTyping(true);
    setSarvamError(null);

    try {
      const apiMessages = messages.map(m => ({ role: m.role, content: m.text }));
      apiMessages.push({ role: 'user', content: input });
      const res = await api.post('/llm/chat', {
        messages: apiMessages
      });
      
      if (res.data.error) {
        setSarvamError(res.data.error);
      } else {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          text: res.data.reply 
        }]);
      }
    } catch (err) {
      setSarvamError("NETWORK_ERROR");
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="h-full flex flex-col max-w-4xl mx-auto">
      <header className="mb-6 text-center">
        <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">AI Assistant</h2>
        <p className="text-white/50 mt-1 font-mono text-sm">LLM Core v2.4 (Sarvam Integrated)</p>
      </header>

      <div className="flex-1 glass-panel rounded-3xl p-6 flex flex-col overflow-hidden relative">
        <div className="flex-1 overflow-y-auto space-y-6 pr-4">
          {messages.map((msg, i) => (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              key={i} 
              className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${
                msg.role === 'assistant' 
                  ? 'bg-gradient-to-br from-blue-600 to-purple-600 shadow-[0_0_15px_rgba(59,130,246,0.4)]' 
                  : 'bg-white/10 border border-white/20'
              }`}>
                {msg.role === 'assistant' ? <Bot className="w-5 h-5 text-white" /> : <User className="w-5 h-5 text-white/70" />}
              </div>
              <div className={`px-5 py-3 rounded-2xl max-w-[80%] ${
                msg.role === 'user'
                  ? 'bg-white/10 text-white'
                  : 'bg-blue-500/10 border border-blue-500/20 text-blue-50'
              }`}>
                {msg.text}
              </div>
            </motion.div>
          ))}
          {isTyping && (
             <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-4"
             >
               <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
                  <Bot className="w-5 h-5 text-white" />
               </div>
               <div className="px-5 py-3 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center gap-1">
                 <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></span>
                 <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                 <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
               </div>
             </motion.div>
          )}
          {sarvamError === 'SERVICE_NOT_CONFIGURED' && (
             <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-center my-4">
                <div className="bg-red-900/20 border border-red-500/20 text-red-400 px-6 py-4 rounded-xl flex items-center gap-3">
                   <AlertTriangle className="w-6 h-6 shrink-0" />
                   <div>
                     <p className="font-semibold">SERVICE_NOT_CONFIGURED</p>
                     <p className="text-sm opacity-80">Sarvam API key is missing. The AI cannot respond.</p>
                   </div>
                </div>
             </motion.div>
          )}
          <div ref={endRef} />
        </div>
        
        <div className="mt-4 pt-4 border-t border-white/10">
          <div className="flex bg-black/40 rounded-full border border-white/10 p-1 pl-4 focus-within:border-blue-500/50 focus-within:shadow-[0_0_20px_rgba(59,130,246,0.2)] transition-all">
            <input 
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask the neural assistant..."
              className="flex-1 bg-transparent border-none outline-none text-white placeholder:text-white/30"
            />
            <button 
              onClick={handleSend}
              className="p-3 bg-white text-black rounded-full hover:bg-gray-200 transition-colors"
            >
              <Send className="w-5 h-5 ml-1" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;
