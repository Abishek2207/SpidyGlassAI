import React, { useState } from 'react';
import { ArrowRightLeft, Volume2, Loader, AlertTriangle } from 'lucide-react';

import { api } from '../App';

const languages = ['English', 'Tamil', 'Hindi'];

const Translation: React.FC = () => {
  const [sourceLang, setSourceLang] = useState('English');
  const [targetLang, setTargetLang] = useState('Tamil');
  const [inputText, setInputText] = useState('Hello, how are you doing today?');
  const [translatedText, setTranslatedText] = useState('வணக்கம், இன்று நீங்கள் எப்படி இருக்கிறீர்கள்?');
  const [isTranslating, setIsTranslating] = useState(false);
  const [sarvamError, setSarvamError] = useState<string | null>(null);

  

  const handleTranslate = async () => {
    setIsTranslating(true);
    try {
      const res = await api.post('/translation/translate', {
        input: inputText,
        source_language_code: "en-IN",
        target_language_code: "hi-IN"
      });
      
      if (res.data.error) {
         setSarvamError(res.data.error);
      } else {
         setSarvamError(null);
         setTranslatedText(res.data.translated_text);
      }
    } catch (err) {
      setSarvamError("NETWORK_ERROR");
    } finally {
      setIsTranslating(false);
    }
  };

  const handleSwap = () => {
    setSourceLang(targetLang);
    setTargetLang(sourceLang);
    setInputText(translatedText);
    setTranslatedText(inputText);
  };

  return (
    <div className="h-full flex flex-col space-y-6">
      <header>
        <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-white/50">Translation Mesh</h2>
        <p className="text-white/50 mt-1">Real-time Sarvam AI translation matrix</p>
      </header>

      <div className="glass-panel rounded-3xl p-8 flex-1 flex flex-col">
        <div className="flex items-center justify-between mb-8 bg-black/40 p-4 rounded-2xl border border-white/5">
          <select 
            value={sourceLang} 
            onChange={(e) => setSourceLang(e.target.value)}
            className="bg-transparent text-xl font-medium outline-none cursor-pointer"
          >
            {languages.map(l => <option key={l} value={l} className="bg-gray-900">{l}</option>)}
          </select>
          
          <button 
            onClick={handleSwap}
            className="p-3 rounded-full bg-white/5 hover:bg-white/10 transition-colors border border-white/10"
          >
            <ArrowRightLeft className="w-5 h-5" />
          </button>
          
          <select 
            value={targetLang} 
            onChange={(e) => setTargetLang(e.target.value)}
            className="bg-transparent text-xl font-medium outline-none cursor-pointer text-right"
          >
            {languages.map(l => <option key={l} value={l} className="bg-gray-900">{l}</option>)}
          </select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 flex-1">
          <div className="flex flex-col relative group">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              className="flex-1 bg-black/20 border border-white/10 rounded-2xl p-6 text-2xl font-light resize-none outline-none focus:border-blue-500/50 transition-colors placeholder:text-white/20"
              placeholder="Type to translate..."
            />
          </div>
          
          <div className="flex flex-col relative">
            <div className={`flex-1 bg-gradient-to-br from-blue-900/10 to-purple-900/10 border ${isTranslating ? 'border-blue-500/50 shadow-[0_0_20px_rgba(59,130,246,0.2)]' : 'border-white/10'} rounded-2xl p-6 transition-all duration-500 relative overflow-hidden`}>
              {sarvamError === 'SERVICE_NOT_CONFIGURED' ? (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-red-400 bg-red-900/20 text-center p-6">
                   <AlertTriangle className="w-10 h-10 mb-4" />
                   <span className="font-semibold text-lg">SERVICE_NOT_CONFIGURED</span>
                   <span className="text-sm mt-2 text-white/50">Cannot reach Sarvam Translation. Check API keys.</span>
                </div>
              ) : isTranslating ? (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-blue-400">
                   <Loader className="w-10 h-10 animate-spin mb-4" />
                   <span className="font-mono text-sm">Processing with Sarvam AI...</span>
                </div>
              ) : (
                <>
                  <p className="text-2xl font-light text-white/90">{translatedText}</p>
                  <button className="absolute bottom-6 right-6 p-3 rounded-full bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 transition-colors">
                    <Volume2 className="w-5 h-5" />
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
        
        <div className="mt-8 flex justify-center">
           <button 
             onClick={handleTranslate}
             disabled={isTranslating}
             className="px-8 py-4 rounded-full bg-white text-black font-semibold text-lg hover:bg-gray-200 transition-colors shadow-[0_0_20px_rgba(255,255,255,0.3)] disabled:opacity-50"
           >
             Translate Sequence
           </button>
        </div>
      </div>
    </div>
  );
};

export default Translation;
