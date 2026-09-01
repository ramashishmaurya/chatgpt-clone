import React, { useState, useRef, useEffect } from 'react';
import {
  MessageSquare,
  Plus,
  User,
  Send,
  Menu,
  Bot,
  MoreHorizontal,
  Paperclip,
  FileText,
  X,
  Trash2
} from 'lucide-react';
import './index.css';

interface Message {
  id: string;
  role: 'user' | 'bot';
  content: string;
}

interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  serverId?: string;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://13.232.214.227:8000';

function App() {
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [input, setInput] = useState('');
  
  const [chats, setChats] = useState<ChatSession[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [isTyping, setIsTyping] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load chat history on mount
  useEffect(() => {
    const fetchChats = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/chats`);
        if (res.ok) {
          const data = await res.json();
          if (data.length > 0) {
            const loadedChats = data.map((c: any) => ({
              id: c.id,
              title: c.title,
              messages: [],
              serverId: c.id
            }));
            setChats(loadedChats);
            
            // Switch to the first chat
            await loadChatMessages(loadedChats[0].id);
          } else {
            createNewChat(); // Start a new chat if database is empty
          }
        }
      } catch (error) {
        console.error("Failed to load chats", error);
        createNewChat();
      }
    };
    fetchChats();
  }, []);

  const currentChat = chats.find(c => c.id === currentChatId) || chats[0];
  const messages = currentChat?.messages || [];

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

  const handleSendMessage = async () => {
    if (!input.trim() || isTyping || isUploading || !currentChat) return;

    const content = input.trim();

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: content,
    };

    setChats(prevChats => prevChats.map(chat => {
      if (chat.id === currentChatId) {
        const isFirstUserMessage = chat.messages.length === 1 && chat.messages[0].role === 'bot';
        const newTitle = isFirstUserMessage ? content.substring(0, 25) + '...' : chat.title;
        return {
          ...chat,
          title: newTitle,
          messages: [...chat.messages, userMessage]
        };
      }
      return chat;
    }));
    
    setInput('');
    setIsTyping(true);

    try {
      // Create JSON payload for chat API
      const payload = {
        session_id: currentChat.serverId || currentChatId,
        question: content
      };

      const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from server');
      }

      const botMessageId = (Date.now() + 1).toString();
      
      // Initialize an empty bot message
      setChats(prevChats => prevChats.map(chat => {
        if (chat.id === currentChatId) {
          return {
            ...chat,
            messages: [...chat.messages, { id: botMessageId, role: 'bot', content: '' }]
          };
        }
        return chat;
      }));

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (reader) {
        let done = false;
        let streamedText = '';
        while (!done) {
          const { value, done: readerDone } = await reader.read();
          done = readerDone;
          if (value) {
            const chunk = decoder.decode(value, { stream: true });
            streamedText += chunk;
            
            // Update the specific bot message
            setChats(prevChats => prevChats.map(chat => {
              if (chat.id === currentChatId) {
                return {
                  ...chat,
                  messages: chat.messages.map(msg => 
                    msg.id === botMessageId ? { ...msg, content: streamedText } : msg
                  )
                };
              }
              return chat;
            }));
          }
        }
      }
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'bot',
        content: 'Error communicating with backend server. Please make sure it is running on port 8000.',
      };
      setChats(prevChats => prevChats.map(chat => {
        if (chat.id === currentChatId) {
          return {
            ...chat,
            messages: [...chat.messages, errorMessage]
          };
        }
        return chat;
      }));
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setIsUploading(true);

      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch(`${API_BASE_URL}/api/upload`, {
          method: 'POST',
          body: formData,
        });

        const data = await response.json();

        if (response.ok) {
          const serverSessionId = data.session_id;
          
          setChats(prev => prev.map(chat => {
            if (chat.id === currentChatId) {
              return { 
                ...chat, 
                serverId: serverSessionId,
                title: file.name.substring(0, 25),
                messages: [
                  ...chat.messages,
                  {
                    id: Date.now().toString(),
                    role: 'bot',
                    content: `File "${file.name}" uploaded successfully. You can now ask questions about it.`
                  }
                ]
              };
            }
            return chat;
          }));
        } else {
          throw new Error(data.detail || 'Upload failed');
        }
      } catch (error: any) {
        console.error("Upload error:", error);
        setChats(prev => prev.map(chat => {
          if (chat.id === currentChatId) {
            return {
              ...chat,
              messages: [
                ...chat.messages,
                {
                  id: Date.now().toString(),
                  role: 'bot',
                  content: `Failed to upload "${file.name}": ${error.message}`
                }
              ]
            };
          }
          return chat;
        }));
        setSelectedFile(null);
      } finally {
        setIsUploading(false);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      }
    }
  };

  const toggleSidebar = () => {
    setSidebarOpen(!isSidebarOpen);
  };

  const createNewChat = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/chat/new`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        const newChat: ChatSession = {
          id: data.id,
          serverId: data.id,
          title: 'New Chat',
          messages: [
            {
              id: '1',
              role: 'bot',
              content: 'Hello! I am a ChatGPT-like AI assistant. You can upload a document and ask me questions about it.',
            }
          ]
        };
        setChats(prev => [newChat, ...prev]);
        setCurrentChatId(data.id);
      }
    } catch(err) {
      // Fallback to local if offline
      const fallbackId = Date.now().toString();
      const newChat: ChatSession = {
        id: fallbackId,
        title: 'New Chat',
        messages: [
          {
            id: '1',
            role: 'bot',
            content: 'Hello! I am a ChatGPT-like AI assistant. You can upload a document and ask me questions about it.',
          }
        ]
      };
      setChats(prev => [newChat, ...prev]);
      setCurrentChatId(fallbackId);
    }
    
    setSelectedFile(null); 
    if (window.innerWidth <= 768) setSidebarOpen(false);
  };

  const loadChatMessages = async (id: string) => {
    setCurrentChatId(id);
    setSelectedFile(null);
    if (window.innerWidth <= 768) setSidebarOpen(false);
    
    try {
      const res = await fetch(`${API_BASE_URL}/api/chat/${id}/messages`);
      if (res.ok) {
        const msgs = await res.json();
        setChats(prev => prev.map(c => {
          if (c.id === id) {
            return {
              ...c,
              messages: msgs.length > 0 ? msgs : [
                {
                  id: '1',
                  role: 'bot',
                  content: 'Hello! I am a ChatGPT-like AI assistant. You can upload a document and ask me questions about it.',
                }
              ]
            };
          }
          return c;
        }));
      }
    } catch (e) {
      console.error("Failed to fetch messages for session:", id);
    }
  };

  const switchChat = (id: string) => {
    loadChatMessages(id);
  };

  const deleteChat = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    
    try {
      await fetch(`${API_BASE_URL}/api/chat/${id}`, {
        method: 'DELETE',
      });
    } catch (error) {
      console.error("Failed to delete chat on backend:", error);
    }
    
    setChats(prev => {
      const newChats = prev.filter(c => c.id !== id);
      if (newChats.length === 0) {
        createNewChat();
        return [];
      }
      
      if (id === currentChatId) {
        loadChatMessages(newChats[0].id);
      }
      return newChats;
    });
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className={`sidebar ${isSidebarOpen ? 'open' : ''}`}>
        <button className="new-chat-btn" onClick={createNewChat}>
          <Plus size={18} />
          New Chat
        </button>

        <div className="chat-history">
          {chats.map(chat => (
            <div 
              key={chat.id} 
              className={`history-item ${chat.id === currentChatId ? 'active' : ''}`}
              onClick={() => switchChat(chat.id)}
              style={chat.id === currentChatId ? { background: 'rgba(255, 255, 255, 0.1)' } : {}}
            >
              <div className="history-item-content">
                <MessageSquare size={16} style={{ flexShrink: 0 }} />
                <span className="history-item-text">
                  {chat.title}
                </span>
              </div>
              <button 
                className="delete-chat-btn"
                onClick={(e) => deleteChat(e, chat.id)}
                title="Delete Chat"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main Area */}
      <div className="main-area">
        <div className="header">
          <button className="menu-btn" onClick={toggleSidebar}>
            <Menu size={24} />
          </button>
          <div style={{ flex: 1 }} />
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
            {selectedFile && (
              <div className="selected-file-preview">
                <FileText size={16} className="file-icon" />
                <span className="file-name">
                  {isUploading ? `Uploading ${selectedFile.name}...` : selectedFile.name}
                </span>
                {!isUploading && (
                  <button className="remove-file-btn" onClick={() => setSelectedFile(null)}>
                    <X size={14} />
                  </button>
                )}
              </div>
            )}
            <div className="input-row">
              <button 
                className="upload-btn" 
                onClick={() => fileInputRef.current?.click()}
                title="Attach file"
                disabled={isUploading}
              >
                <Paperclip size={18} />
              </button>
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileSelect} 
                style={{ display: 'none' }} 
              />
              <textarea
                ref={textareaRef}
                className="chat-input"
                placeholder="Message ChatGPT..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
                disabled={isUploading}
              />
              <button
                className="submit-btn"
                onClick={handleSendMessage}
                disabled={!input.trim() || isTyping || isUploading}
              >
                <Send size={16} />
              </button>
            </div>
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
