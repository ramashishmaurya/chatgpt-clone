import React, { useState, useRef, useEffect } from 'react';
import { 
  MessageSquare, 
  Plus, 
  Settings, 
  User, 
  Send, 
  Menu,
  Bot,
  MoreHorizontal
} from 'lucide-react';
import './index.css';

interface Message {
  id: string;
  role: 'user' | 'bot';
  content: string;
}

function App() {
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'bot',
      content: 'Hello! I am a ChatGPT-like AI assistant. How can I help you today?',
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const handleSendMessage = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'bot',
        content: `I'm a simulated AI. You said: "${userMessage.content}". This is a demonstration of the UI!`,
      };
      setMessages(prev => [...prev, botMessage]);
      setIsTyping(false);
    }, 1500);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const toggleSidebar = () => {
    setSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className={`sidebar ${isSidebarOpen ? 'open' : ''}`}>
        <button className="new-chat-btn" onClick={() => setMessages([])}>
          <Plus size={18} />
          New Chat
        </button>
        
        <div className="chat-history">
          <div className="history-item">
            <MessageSquare size={16} />
            <span>Understanding Quantum Mechanics</span>
          </div>
          <div className="history-item">
            <MessageSquare size={16} />
            <span>Dinner Recipe Ideas</span>
          </div>
          <div className="history-item">
            <MessageSquare size={16} />
            <span>Debug React Hook</span>
          </div>
        </div>

        <div className="sidebar-bottom">
          <div className="history-item">
            <Settings size={16} />
            <span>Settings</span>
          </div>
          <div className="user-profile">
            <div className="avatar bot" style={{ width: '24px', height: '24px', borderRadius: '50%'}}>
              <User size={14} />
            </div>
            <span>User Name</span>
          </div>
        </div>
      </div>

      {/* Main Area */}
      <div className="main-area">
        <div className="header">
          <button className="menu-btn" onClick={toggleSidebar}>
            <Menu size={24} />
          </button>
          <div style={{ flex: 1 }} />
          {/* Optional header actions can go here */}
        </div>

        <div className="chat-container">
          {messages.map((msg) => (
            <div key={msg.id} className={`message-wrapper ${msg.role}`}>
              <div className="message-inner">
                {msg.role === 'bot' && (
                  <div className="avatar bot">
                    <Bot size={20} />
                  </div>
                )}
                
                <div className="message-content">
                  {msg.content}
                </div>

                {msg.role === 'user' && (
                   <div className="avatar user">
                    <User size={20} />
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isTyping && (
             <div className="message-wrapper bot">
             <div className="message-inner">
               <div className="avatar bot">
                 <Bot size={20} />
               </div>
               <div className="message-content" style={{ display: 'flex', alignItems: 'center', gap: '4px', height: '24px' }}>
                 <MoreHorizontal size={24} className="typing-indicator" color="var(--text-secondary)" />
               </div>
             </div>
           </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area-container">
          <div className="input-wrapper">
            <textarea
              ref={textareaRef}
              className="chat-input"
              placeholder="Message ChatGPT..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
            />
            <button 
              className="submit-btn" 
              onClick={handleSendMessage}
              disabled={!input.trim() || isTyping}
            >
              <Send size={16} />
            </button>
          </div>
          <div className="disclaimer">
            ChatGPT can make mistakes. Consider verifying important information.
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
