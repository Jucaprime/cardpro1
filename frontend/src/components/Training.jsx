import React, { useState, useEffect } from 'react';
import { getStats, trainModel } from '../services/api';
import { Brain, Database, RefreshCcw, TrendingUp } from 'lucide-react';

import { motion } from 'framer-motion';

export default function Training() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [trainStatus, setTrainStatus] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const data = await getStats();
      setStats(data);
    } catch (error) {
      console.error("Error fetching stats", error);
    }
  };

  const handleRetrain = async () => {
    setLoading(true);
    setTrainStatus(null);
    try {
      const res = await trainModel();
      setTrainStatus(res);
      fetchStats();
    } catch (error) {
      console.error("Error training model", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <header className="mb-8 relative z-10 text-center">
        <h2 className="text-3xl font-bold tracking-tight">Treinamento do Motor de IA</h2>
        <p className="text-gray-400 mt-2">Monitore o desempenho do modelo e acione o retreinamento manual.</p>
      </header>

      {/* Futuristic Data Feeding Core */}
      <div className="flex justify-center my-20 relative h-64 w-64 mx-auto">
        
        {/* Core Glow */}
        <div className="absolute inset-12 bg-neon-green/20 rounded-full blur-3xl animate-pulse" />
        
        {/* Converging Data Particles (Framer Motion) */}
        {[...Array(16)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute top-1/2 left-1/2 w-2 h-2 bg-neon-green shadow-[0_0_10px_#39FF14] rounded-sm z-20"
            initial={{ 
              x: Math.cos((i * 22.5) * Math.PI / 180) * 180 - 4, 
              y: Math.sin((i * 22.5) * Math.PI / 180) * 180 - 4,
              opacity: 0,
              scale: 0.5
            }}
            animate={{ 
              x: -4, 
              y: -4,
              opacity: [0, 1, 0],
              scale: [0.5, 1.5, 0.5]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              delay: (i % 4) * 0.5 + Math.random() * 0.5, // Staggered delays for a chaotic data flow feel
              ease: "circIn"
            }}
          />
        ))}

        {/* Central Core Container */}
        <div className="absolute inset-14 bg-gray-950 border border-gray-800 shadow-[0_0_40px_rgba(57,255,20,0.15)] rounded-full flex items-center justify-center z-10 overflow-hidden">
          {/* Rotating Processing Rings */}
          <motion.div 
            className="absolute inset-0 border-[3px] border-t-neon-green border-r-transparent border-b-blue-500 border-l-transparent rounded-full opacity-80"
            animate={{ rotate: 360 }}
            transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
          />
          <motion.div 
            className="absolute inset-2 border-[2px] border-t-transparent border-r-neon-green border-b-transparent border-l-blue-500 rounded-full opacity-60"
            animate={{ rotate: -360 }}
            transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
          />
          <Brain size={48} strokeWidth={1.5} className="text-neon-green drop-shadow-[0_0_15px_rgba(57,255,20,1)] animate-pulse" />
        </div>

        {/* Outer Tech/Data Rings */}
        <div className="absolute inset-0 border-[1px] border-dashed border-gray-600/50 rounded-full animate-[spin_20s_linear_infinite]" />
        <div className="absolute inset-[-20px] border-[2px] border-dotted border-neon-green/30 rounded-full animate-[spin_15s_linear_infinite_reverse]" />
        
        {/* Floating Data Blocks (Background) */}
        <div className="absolute inset-[-40px] rounded-full overflow-hidden pointer-events-none mix-blend-screen opacity-30">
           <div className="w-full h-[200%] bg-[linear-gradient(rgba(0,0,0,0)_60%,rgba(57,255,20,0.2)_60%)] bg-[length:100%_10px] animate-[slide_3s_linear_infinite]" />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">
        <div className="glass-card p-6 border-t-4 border-t-neon-green">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm text-gray-400 uppercase tracking-wider font-bold">Precisão</h3>
            <TrendingUp className="text-neon-green" size={20} />
          </div>
          <div className="text-4xl font-black text-white">
            {stats ? stats.accuracy : '--'}%
          </div>
          <p className="text-xs text-gray-500 mt-2">Baseado no feedback do usuário</p>
        </div>

        <div className="glass-card p-6 border-t-4 border-t-blue-500">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm text-gray-400 uppercase tracking-wider font-bold">Base de Conhecimento</h3>
            <Database className="text-blue-500" size={20} />
          </div>
          <div className="text-4xl font-black text-white">
            {stats ? stats.games_learned : '--'}
          </div>
          <p className="text-xs text-gray-500 mt-2">Partidas aprendidas</p>
        </div>

        <button 
          onClick={handleRetrain} 
          disabled={loading}
          className="relative glass-card p-6 w-full h-full min-h-[140px] flex flex-col items-center justify-center overflow-hidden group transition-all duration-500 hover:scale-[1.02] hover:shadow-[0_0_30px_rgba(57,255,20,0.2)] hover:border-neon-green/50 disabled:opacity-70 disabled:hover:scale-100 disabled:hover:shadow-none cursor-pointer"
        >
          {/* Animated glow background on hover */}
          <div className="absolute inset-0 bg-gradient-to-br from-neon-green/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
          
          {/* Scanline light sweep effect on hover */}
          <div className="absolute top-0 -inset-full h-full w-1/2 z-0 block transform -skew-x-12 bg-gradient-to-r from-transparent to-white opacity-10 group-hover:animate-[slide_1.5s_ease-in-out_infinite]" />
          
          <RefreshCcw size={42} strokeWidth={1.5} className={`mb-4 relative z-10 ${loading ? 'text-neon-green animate-spin' : 'text-gray-500 group-hover:text-neon-green group-hover:rotate-180 transition-all duration-700'}`} />
          
          <span className={`relative z-10 font-black uppercase tracking-widest text-sm transition-colors duration-300 ${loading ? 'text-neon-green animate-pulse' : 'text-gray-400 group-hover:text-white'}`}>
            {loading ? 'Compilando Dados...' : 'Acionar Retreinamento'}
          </span>
        </button>
      </div>

      {trainStatus && (
        <div className={`mt-8 p-6 rounded-xl border ${trainStatus.error ? 'bg-red-500/10 border-red-500/50 text-red-400' : 'bg-green-500/10 border-green-500/50 text-green-400'}`}>
          <h3 className="font-bold flex items-center mb-2">
            <Brain className="mr-2" size={20} />
            Resultado do Treinamento
          </h3>
          {trainStatus.error ? (
            <p>{trainStatus.error}</p>
          ) : (
            <p>Modelo retreinado com sucesso. Nova precisão base no conjunto de treinamento: <span className="font-bold text-white">{trainStatus.accuracy.toFixed(1)}%</span> a partir de {trainStatus.games_learned} partidas.</p>
          )}
        </div>
      )}
    </div>
  );
}
