import React, { useState, useEffect } from 'react';
import { getHistory, submitFeedback } from '../services/api';
import { Check, X, RefreshCw } from 'lucide-react';

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await getHistory();
      setHistory(data);
    } catch (error) {
      console.error("Failed to load history", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const [actualCardsInput, setActualCardsInput] = useState({});

  const handleCardsChange = (id, value) => {
    setActualCardsInput(prev => ({...prev, [id]: value}));
  };

  const handleFeedback = async (id) => {
    const cards = parseFloat(actualCardsInput[id]);
    if (isNaN(cards)) return;
    try {
      await submitFeedback(id, null, cards);
      // Refresh
      fetchHistory();
    } catch (error) {
      console.error("Failed to submit feedback", error);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header className="mb-8 flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Histórico de Previsões</h2>
          <p className="text-gray-400 mt-2">Registro de análises passadas e feedback de aprendizado da IA.</p>
        </div>
        <button onClick={fetchHistory} className="text-neon-green hover:text-white transition-colors flex items-center bg-gray-900 border border-gray-800 p-2 rounded">
          <RefreshCw size={18} className={loading ? "animate-spin mr-2" : "mr-2"} />
          Atualizar
        </button>
      </header>

      <div className="glass-card overflow-auto" style={{ maxHeight: 'calc(100vh - 200px)' }}>
        <table className="w-full text-left text-sm text-gray-400 relative">
          <thead className="bg-gray-900/90 text-xs uppercase text-gray-500 border-b border-gray-800 sticky top-0 z-10 backdrop-blur-md">
            <tr>
              <th className="px-6 py-4">ID / Jogo / Data</th>
              <th className="px-6 py-4">Métricas (C/F/Árb)</th>
              <th className="px-6 py-4">Odds (M/m)</th>
              <th className="px-6 py-4">Previsão</th>
              <th className="px-6 py-4">Confiança</th>
              <th className="px-6 py-4">Feedback</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/50">
            {history.length === 0 ? (
              <tr>
                <td colSpan="6" className="text-center py-8">Nenhum histórico encontrado.</td>
              </tr>
            ) : history.map((item) => (
              <tr key={item.id} className="hover:bg-gray-800/20 transition-colors">
                <td className="px-6 py-4">
                  <div className="font-bold text-gray-300">#{item.id} - {item.home_team || 'Casa'} vs {item.away_team || 'Fora'}</div>
                  <div className="text-xs text-gray-500">{new Date(item.created_at).toLocaleDateString()}</div>
                </td>
                <td className="px-6 py-4">
                  {item.home_cards_avg.toFixed(1)} / {item.away_cards_avg.toFixed(1)} / {item.referee_avg.toFixed(1)}
                </td>
                <td className="px-6 py-4">
                  {item.odds_over.toFixed(2)} / {item.odds_under.toFixed(2)}
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${item.prediction.startsWith('OVER') ? 'bg-neon-green/20 text-neon-green border border-neon-green/50' : 'bg-blue-500/20 text-blue-400 border border-blue-500/50'}`}>
                    {item.prediction.replace('OVER', 'MAIS DE').replace('UNDER', 'MENOS DE')}
                  </span>
                </td>
                <td className="px-6 py-4 font-bold text-white">
                  {item.confidence.toFixed(1)}%
                </td>
                <td className="px-6 py-4">
                  {item.actual_cards !== null && item.actual_cards !== undefined ? (
                    <span className="flex items-center text-xs font-bold text-neon-green">
                      <Check size={16} className="mr-1" />
                      {item.actual_cards} Cartões (Mestre)
                    </span>
                  ) : item.is_correct !== null ? (
                    <span className={`flex items-center text-xs font-bold ${item.is_correct ? 'text-green-500' : 'text-red-500'}`}>
                      {item.is_correct ? <Check size={16} className="mr-1" /> : <X size={16} className="mr-1" />}
                      {item.is_correct ? 'Correto' : 'Incorreto'}
                    </span>
                  ) : (
                    <div className="flex space-x-2 items-center">
                      <input 
                        type="number" 
                        placeholder="Qtd exata..."
                        className="w-24 bg-gray-950 border border-gray-700 rounded p-1 text-sm text-white focus:border-neon-green outline-none"
                        value={actualCardsInput[item.id] || ''}
                        onChange={(e) => handleCardsChange(item.id, e.target.value)}
                      />
                      <button onClick={() => handleFeedback(item.id)} className="p-1.5 bg-neon-green/10 hover:bg-neon-green/30 text-neon-green rounded border border-neon-green/30 transition-colors" title="Enviar Resultado">
                        <Check size={16} />
                      </button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
