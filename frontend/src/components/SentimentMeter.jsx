import { Frown, Meh, Smile } from 'lucide-react';

const SentimentMeter = ({ score, label }) => {
  const percentage = ((score + 1) / 2) * 100;
  
  const getSentimentColor = () => {
    if (score < -0.3) return 'bg-red-500';
    if (score > 0.3) return 'bg-green-500';
    return 'bg-yellow-500';
  };
  
  const getSentimentIcon = () => {
    if (score < -0.3) return <Frown className="text-red-500" size={32} />;
    if (score > 0.3) return <Smile className="text-green-500" size={32} />;
    return <Meh className="text-yellow-500" size={32} />;
  };
  
  const getSentimentText = () => {
    if (score < -0.5) return 'Very Negative';
    if (score < -0.3) return 'Negative';
    if (score < 0.3) return 'Neutral';
    if (score < 0.5) return 'Positive';
    return 'Very Positive';
  };
  
  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <div className="flex items-center justify-center mb-4">
        {getSentimentIcon()}
      </div>
      
      <div className="text-center mb-4">
        <p className="text-2xl font-bold text-gray-800 capitalize">{label}</p>
        <p className="text-sm text-gray-600">{getSentimentText()}</p>
      </div>
      
      <div className="relative">
        <div className="w-full h-6 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${getSentimentColor()}`}
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
        
        <div className="flex justify-between mt-2 text-xs text-gray-500">
          <span>Negative</span>
          <span>Neutral</span>
          <span>Positive</span>
        </div>
      </div>
      
      <div className="mt-4 text-center">
        <p className="text-sm text-gray-600">Score</p>
        <p className="text-xl font-bold text-gray-800">{score.toFixed(2)}</p>
      </div>
      
      {score < -0.5 && (
        <div className="mt-4 bg-red-100 border border-red-300 rounded-lg p-3">
          <p className="text-sm text-red-700 font-semibold">⚠️ High Priority</p>
          <p className="text-xs text-red-600 mt-1">Customer appears frustrated.</p>
        </div>
      )}
    </div>
  );
};

export default SentimentMeter;