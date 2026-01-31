import { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import { MessageSquare, BarChart3 } from 'lucide-react';

function App() {
  const [currentView, setCurrentView] = useState('chat');
  
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navigation Header */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-xl font-bold text-gray-900">AI Support Agent</h1>
              </div>
              <div className="ml-6 flex space-x-8">
                <button
                  onClick={() => setCurrentView('chat')}
                  className={`inline-flex items-center px-3 py-2 border-b-2 text-sm font-medium ${
                    currentView === 'chat'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <MessageSquare size={18} className="mr-2" />
                  Chat Interface
                </button>
                <button
                  onClick={() => setCurrentView('analytics')}
                  className={`inline-flex items-center px-3 py-2 border-b-2 text-sm font-medium ${
                    currentView === 'analytics'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <BarChart3 size={18} className="mr-2" />
                  Analytics Dashboard
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>
      
      {/* Main Content */}
      <main>
        {currentView === 'chat' ? <ChatInterface /> : <AnalyticsDashboard />}
      </main>
    </div>
  );
}

export default App;
