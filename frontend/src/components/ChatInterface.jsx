import { useState, useEffect, useRef } from 'react';
import { sendMessage } from '../services/api';
import { Send, User, Bot } from 'lucide-react';
import SentimentMeter from './SentimentMeter';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [currentSentiment, setCurrentSentiment] = useState({ score: 0, label: 'neutral' });
  const [customerName, setCustomerName] = useState('');
  const [showNameInput, setShowNameInput] = useState(true);
  const [isEscalated, setIsEscalated] = useState(false);
  
  const messagesEndRef = useRef(null);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const handleStartChat = () => {
    if (customerName.trim()) {
      setShowNameInput(false);
      setMessages([
        {
          role: 'assistant',
          content: `Hello ${customerName}! I'm here to help you. How can I assist you today?`,
          timestamp: new Date(),
        },
      ]);
    }
  };
  
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;
    
    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    
    try {
      const response = await sendMessage(sessionId, inputMessage, customerName);
      
      setCurrentSentiment({
        score: response.sentiment_score,
        label: response.sentiment_label,
      });
      
      if (response.should_escalate) {
        setIsEscalated(true);
      }
      
      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (showNameInput) {
        handleStartChat();
      } else {
        handleSendMessage();
      }
    }
  };
  
  if (showNameInput) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Welcome to Support Chat</h2>
          <p className="text-gray-600 mb-6">Please enter your name to get started</p>
          <input
            type="text"
            value={customerName}
            onChange={(e) => setCustomerName(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Your name"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
          />
          <button
            onClick={handleStartChat}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            Start Chat
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="flex h-screen bg-gray-100">
      <div className="flex-1 flex flex-col">
        <div className="bg-white border-b px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-800">Customer Support</h1>
            <p className="text-sm text-gray-500">Session: {sessionId.substring(0, 20)}...</p>
          </div>
          {isEscalated && (
            <div className="bg-red-100 text-red-700 px-4 py-2 rounded-lg font-semibold">
              🚨 Escalated to Human Agent
            </div>
          )}
        </div>
        
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} group`}
            >
              <div className={`flex items-start space-x-2 max-w-2xl transition-all duration-200 ${msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                <div className={`p-2 rounded-full ${msg.role === 'user' ? 'bg-blue-600' : 'bg-gray-300'} group-hover:scale-110 transition-transform`}>
                  {msg.role === 'user' ? <User size={20} className="text-white" /> : <Bot size={20} className="text-gray-700" />}
                </div>
                <div>
                  <div
                    className={`px-4 py-3 rounded-2xl transition-all duration-200 ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white group-hover:bg-blue-700 group-hover:shadow-lg'
                        : 'bg-white text-gray-800 border border-gray-200 group-hover:shadow-md group-hover:border-gray-300'
                    }`}
                  >
                    {msg.content}
                  </div>
                  <p className="text-xs text-gray-400 mt-1">
                    {msg.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex items-start space-x-2 max-w-2xl">
                <div className="p-2 rounded-full bg-gray-300">
                  <Bot size={20} className="text-gray-700" />
                </div>
                <div className="bg-white rounded-2xl px-6 py-4 border border-gray-200 shadow-sm">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></div>
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></div>
                    </div>
                    <span className="text-sm text-gray-500 ml-2">AI is thinking...</span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        <div className="bg-white border-t px-6 py-4">
          <div className="flex space-x-4">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
      
      <div className="w-80 bg-white border-l p-6">
        <h3 className="text-lg font-semibold mb-4">Live Sentiment Analysis</h3>
        <SentimentMeter score={currentSentiment.score} label={currentSentiment.label} />
        
        <div className="mt-6">
          <h4 className="font-semibold mb-2">Customer Info</h4>
          <p className="text-sm text-gray-600">Name: {customerName}</p>
          <p className="text-sm text-gray-600">Messages: {messages.filter(m => m.role === 'user').length}</p>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;