import { useState } from "react";
import { X } from "lucide-react";
import { getMistralKey } from "../utils/keys";

export default function ChatPanel({ open, onClose }) {
  const [messages, setMessages] = useState([{ role: 'bot', content: 'Ask about environment, climate, or air quality.' }]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  function add(role, content) { setMessages((m)=>[...m, { role, content }]); }

  async function send() {
    const msg = input.trim(); if (!msg) return; setInput(""); add('user', msg);
    const key = getMistralKey(); if (!key) { add('bot','Set Mistral key in localStorage("mistral.key") or env.'); return; }
    setSending(true);
    try {
      const resp = await fetch('https://api.mistral.ai/v1/chat/completions', {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${key}` },
        body: JSON.stringify({ model: 'mistral-tiny', messages: [ { role:'system', content:'Environmental assistant. Stay on env/climate/air topics.' }, { role:'user', content: msg } ] })
      });
      const data = await resp.json(); const text = data?.choices?.[0]?.message?.content || 'No response.'; add('bot', text);
    } catch { add('bot','Connection error.'); } finally { setSending(false); }
  }

  if (!open) return null;
  return (
    <div className="absolute bottom-5 right-5 w-96 max-w-[95%] h-[500px] bg-white rounded-2xl shadow-xl flex flex-col z-20">
      <div className="bg-blue-600 text-white px-4 py-3 flex items-center justify-between rounded-t-2xl">
        <span className="font-semibold">🌍 Environment Chat</span>
        <button onClick={onClose} className="text-white/90 hover:text-white"><X size={20} /></button>
      </div>
      <div className="flex-1 overflow-y-auto p-4 bg-slate-100">
        {messages.map((m,i)=> (
          <div key={i} className={`max-w-[80%] mb-3 px-3 py-2 rounded-xl text-sm ${m.role==='user' ? 'ml-auto bg-blue-600 text-white':'mr-auto bg-white text-slate-800 border border-slate-200'}`}>{m.content}</div>
        ))}
      </div>
      <div className="p-3 border-t border-slate-200 flex items-center gap-2 bg-white">
        <input value={input} onChange={(e)=>setInput(e.target.value)} onKeyDown={(e)=>{ if(e.key==='Enter') send(); }} className="flex-1 border border-slate-300 rounded-full px-3 py-2 text-sm outline-none" placeholder="Ask about environment, climate, air quality..." />
        <button onClick={send} disabled={sending} className={`rounded-full w-10 h-10 grid place-items-center text-white ${sending?'bg-slate-400':'bg-blue-600 hover:bg-blue-500'}`}>➤</button>
      </div>
    </div>
  );
}
