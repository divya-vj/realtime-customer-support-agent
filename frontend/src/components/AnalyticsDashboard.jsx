import { useState, useEffect } from 'react';
import { getDashboardAnalytics, getAllConversations, getSentimentTrends } from '../services/api';
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, MessageSquare, CheckCircle, AlertTriangle, RefreshCw } from 'lucide-react';

const AnalyticsDashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [sentimentTrends, setSentimentTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchAnalytics();
  }, []);
  
  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const [analyticsData, conversationsData, trendsData] = await Promise.all([
        getDashboardAnalytics(),
        getAllConversations(),
        getSentimentTrends(),
      ]);
      
      setAnalytics(analyticsData);
      setConversations(conversationsData);
      setSentimentTrends(trendsData.trends || []);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <RefreshCw className="animate-spin mx-auto mb-4 text-blue-600" size={48} />
          <p className="text-xl text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }
  
  const sentimentPieData = analytics ? [
    { name: 'Positive', value: analytics.sentiment_distribution.positive, color: '#10b981' },
    { name: 'Neutral', value: analytics.sentiment_distribution.neutral, color: '#f59e0b' },
    { name: 'Negative', value: analytics.sentiment_distribution.negative, color: '#ef4444' },
  ] : [];
  
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
            <p className="text-gray-600 mt-2">Real-time insights into customer support performance</p>
          </div>
          <button
            onClick={fetchAnalytics}
            className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <RefreshCw size={18} />
            <span>Refresh</span>
          </button>
        </div>
        
        {/* Metric Cards with Staggered Animation */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="animate-fadeIn" style={{ animationDelay: '0.1s' }}>
            <MetricCard
              title="Total Conversations"
              value={analytics?.total_conversations || 0}
              icon={<MessageSquare size={24} />}
              color="bg-blue-500"
            />
          </div>
          <div className="animate-fadeIn" style={{ animationDelay: '0.2s' }}>
            <MetricCard
              title="Resolution Rate"
              value={`${analytics?.resolution_rate || 0}%`}
              icon={<CheckCircle size={24} />}
              color="bg-green-500"
            />
          </div>
          <div className="animate-fadeIn" style={{ animationDelay: '0.3s' }}>
            <MetricCard
              title="Escalated"
              value={analytics?.escalated_conversations || 0}
              icon={<AlertTriangle size={24} />}
              color="bg-red-500"
            />
          </div>
          <div className="animate-fadeIn" style={{ animationDelay: '0.4s' }}>
            <MetricCard
              title="Avg Sentiment"
              value={analytics?.average_sentiment?.toFixed(2) || '0.00'}
              icon={<TrendingUp size={24} />}
              color="bg-purple-500"
            />
          </div>
        </div>
        
        {/* Charts with Animation */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="animate-fadeIn" style={{ animationDelay: '0.5s' }}>
            <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
              <h3 className="text-lg font-semibold mb-4">Sentiment Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={sentimentPieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {sentimentPieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          <div className="animate-fadeIn" style={{ animationDelay: '0.6s' }}>
            <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
              <h3 className="text-lg font-semibold mb-4">Sentiment Over Time</h3>
              {sentimentTrends.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={sentimentTrends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis domain={[-1, 1]} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="sentiment" stroke="#8b5cf6" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-[300px] text-gray-400">
                  No trend data available yet
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Common Issues with Animation */}
        <div className="bg-white rounded-lg shadow p-6 mb-8 animate-fadeIn hover:shadow-lg transition-shadow" style={{ animationDelay: '0.7s' }}>
          <h3 className="text-lg font-semibold mb-4">Common Issues</h3>
          <div className="flex flex-wrap gap-2">
            {analytics?.common_issues?.map((issue, idx) => (
              <span
                key={idx}
                className="px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm font-medium capitalize hover:bg-blue-200 transition-colors cursor-pointer"
              >
                {issue}
              </span>
            ))}
          </div>
        </div>
        
        {/* Recent Conversations Table with Animation */}
        <div className="bg-white rounded-lg shadow p-6 animate-fadeIn hover:shadow-lg transition-shadow" style={{ animationDelay: '0.8s' }}>
          <h3 className="text-lg font-semibold mb-4">Recent Conversations</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Session ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sentiment</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {conversations.length > 0 ? conversations.slice(0, 10).map((conv) => (
                  <tr key={conv.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 text-sm text-gray-900">{conv.session_id.substring(0, 20)}...</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{conv.customer_name || 'Anonymous'}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        conv.status === 'resolved' ? 'bg-green-100 text-green-700' :
                        conv.status === 'escalated' ? 'bg-red-100 text-red-700' :
                        'bg-yellow-100 text-yellow-700'
                      }`}>
                        {conv.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span className={`font-semibold ${
                        conv.average_sentiment > 0.3 ? 'text-green-600' :
                        conv.average_sentiment < -0.3 ? 'text-red-600' :
                        'text-yellow-600'
                      }`}>
                        {conv.average_sentiment !== null ? conv.average_sentiment.toFixed(2) : 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {new Date(conv.created_at).toLocaleString()}
                    </td>
                  </tr>
                )) : (
                  <tr>
                    <td colSpan="5" className="px-6 py-8 text-center text-gray-400">
                      No conversations yet. Start chatting to see data!
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

const MetricCard = ({ title, value, icon, color }) => {
  return (
    <div className="bg-white rounded-lg shadow p-6 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 cursor-pointer transform">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        </div>
        <div className={`${color} p-3 rounded-lg text-white transition-transform hover:scale-110`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;