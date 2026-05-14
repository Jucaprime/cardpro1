import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Activity, History, Settings, PlaySquare } from 'lucide-react';
import Dashboard from './components/Dashboard';
import HistoryView from './components/History';
import Training from './components/Training';

function AppContent() {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Painel', icon: Activity },
    { path: '/history', label: 'Histórico', icon: History },
    { path: '/training', label: 'Treinamento', icon: PlaySquare },
    { path: '/settings', label: 'Configurações', icon: Settings },
  ];

  return (
    <div className="flex min-h-screen bg-gray-950 text-gray-100 font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-gray-800 bg-gray-900/50 p-6 flex flex-col">
        <div className="mb-10">
          <h1 className="text-2xl font-bold neon-text tracking-wider">Card Pro</h1>
          <p className="text-xs text-gray-400 mt-1 uppercase tracking-widest">Análise de dados</p>
        </div>
        
        <nav className="flex-1 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                  isActive 
                    ? 'bg-gray-800/80 text-neon-green border border-neon-green/30 shadow-[0_0_10px_rgba(57,255,20,0.1)]' 
                    : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
                }`}
              >
                <Icon size={20} className={isActive ? 'text-neon-green' : ''} />
                <span className="font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>
        
        <div className="pt-6 border-t border-gray-800">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-400">Status do Sistema</span>
            <span className="flex items-center text-neon-green">
              <span className="w-2 h-2 rounded-full bg-neon-green mr-2 animate-pulse"></span>
              Online
            </span>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/history" element={<HistoryView />} />
          <Route path="/training" element={<Training />} />
          <Route path="/settings" element={<div className="glass-card p-8"><h2 className="text-xl font-bold neon-text mb-4">Configurações</h2><p className="text-gray-400">Simulação da configuração da URL da API.</p></div>} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}
