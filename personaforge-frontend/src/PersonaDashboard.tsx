import React from 'react';
import { Sparkles, Download, BarChart3, User, MessageCircle, TrendingUp } from 'lucide-react';

const PersonaDashboard = () => {
  return (
    <section className="py-20 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent mb-4">
            Sample Persona Analysis
          </h2>
          <p className="text-xl text-white/70 max-w-2xl mx-auto">
            Enter a Reddit username above to generate a real persona with detailed insights and visualizations.
          </p>
        </div>

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Persona Overview Card */}
          <div className="lg:col-span-2">
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                    <User className="w-8 h-8 text-white" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-white">u/RedditUser123</h3>
                    <p className="text-white/60">Active Redditor • 2.5k karma</p>
                  </div>
                </div>
                <div className="bg-green-500/20 border border-green-500/30 rounded-full px-4 py-2">
                  <span className="text-green-400 font-semibold">Active</span>
                </div>
              </div>

              {/* Personality Traits */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <div className="bg-white/5 rounded-xl p-4 text-center">
                  <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center mx-auto mb-2">
                    <TrendingUp className="w-4 h-4 text-blue-400" />
                  </div>
                  <p className="text-sm text-white/60">Analytical</p>
                  <p className="text-lg font-bold text-white">85%</p>
                </div>
                <div className="bg-white/5 rounded-xl p-4 text-center">
                  <div className="w-8 h-8 bg-green-500/20 rounded-lg flex items-center justify-center mx-auto mb-2">
                    <MessageCircle className="w-4 h-4 text-green-400" />
                  </div>
                  <p className="text-sm text-white/60">Social</p>
                  <p className="text-lg font-bold text-white">72%</p>
                </div>
                <div className="bg-white/5 rounded-xl p-4 text-center">
                  <div className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center mx-auto mb-2">
                    <Sparkles className="w-4 h-4 text-purple-400" />
                  </div>
                  <p className="text-sm text-white/60">Creative</p>
                  <p className="text-lg font-bold text-white">68%</p>
                </div>
                <div className="bg-white/5 rounded-xl p-4 text-center">
                  <div className="w-8 h-8 bg-orange-500/20 rounded-lg flex items-center justify-center mx-auto mb-2">
                    <BarChart3 className="w-4 h-4 text-orange-400" />
                  </div>
                  <p className="text-sm text-white/60">Technical</p>
                  <p className="text-lg font-bold text-white">91%</p>
                </div>
              </div>

              {/* Quote */}
              <blockquote className="bg-gradient-to-r from-purple-500/10 to-blue-500/10 border-l-4 border-purple-500 p-6 rounded-r-xl">
                <p className="text-lg italic text-white/90 mb-2">
                  "This user shows strong analytical thinking patterns, often engaging in technical discussions with a collaborative approach."
                </p>
                <p className="text-white/60">— AI Analysis</p>
              </blockquote>
            </div>
          </div>

          {/* Quick Stats Card */}
          <div className="space-y-6">
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-6 shadow-2xl">
              <h4 className="text-xl font-semibold text-white mb-4">Quick Stats</h4>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-white/70">Posts</span>
                  <span className="text-white font-semibold">247</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white/70">Comments</span>
                  <span className="text-white font-semibold">1,892</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white/70">Subreddits</span>
                  <span className="text-white font-semibold">23</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-white/70">Account Age</span>
                  <span className="text-white font-semibold">2.3 years</span>
                </div>
              </div>
            </div>

            {/* Export Button */}
            <div className="bg-gradient-to-r from-purple-500/20 to-blue-500/20 border border-purple-500/30 rounded-3xl p-6">
              <h4 className="text-xl font-semibold text-white mb-4">Export Options</h4>
              <div className="space-y-3">
                <button className="w-full bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 text-white px-4 py-3 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105 flex items-center justify-center gap-2">
                  <Download className="w-5 h-5" />
                  Export PDF
                </button>
                <button className="w-full bg-white/10 hover:bg-white/20 text-white px-4 py-3 rounded-xl font-semibold transition-all duration-300 border border-white/20 flex items-center justify-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  View Charts
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default PersonaDashboard; 