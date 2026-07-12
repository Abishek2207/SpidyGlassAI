import { motion, AnimatePresence } from 'framer-motion';
import { History, MessageSquare, Bot } from 'lucide-react';
import type { AgentResponse } from '../App';

export const ConversationHistory = ({ history }: { history: AgentResponse[] }) => {
  return (
    <motion.div 
      initial={{ x: -50, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="w-full lg:w-80 glass-panel rounded-3xl p-5 flex flex-col h-full overflow-hidden border border-white/5"
    >
      <h3 className="text-sm font-semibold tracking-widest text-neutral-400 uppercase mb-4 flex items-center gap-2">
        <History className="w-4 h-4" /> HUD Log
      </h3>
      
      <div className="flex-1 overflow-y-auto pr-2 flex flex-col gap-4">
        <AnimatePresence>
          {history.length === 0 && (
            <p className="text-sm text-neutral-500 font-light italic text-center mt-10">
              No recent activity.
            </p>
          )}
          {history.map((item, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white/5 rounded-2xl p-3 text-sm flex flex-col gap-2"
            >
              {(item.transcript || item.gesture_detected) && (
                <div className="flex gap-2 text-cyan-300 items-start">
                  <MessageSquare className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <p>{item.transcript || item.gesture_detected}</p>
                </div>
              )}
              {item.ai_reply && (
                <div className="flex gap-2 text-purple-300 items-start mt-1">
                  <Bot className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <p className="text-neutral-300">{item.ai_reply}</p>
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};
