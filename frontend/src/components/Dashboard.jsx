import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { predictCards } from '../services/api';
import { Target, Zap, AlertTriangle, ChevronRight, Download, Activity } from 'lucide-react';

export default function Dashboard() {
  const [formData, setFormData] = useState({
    home_team: '',
    away_team: '',
    home_cards_avg: 2.5,
    away_cards_avg: 2.1,
    referee_avg: 5.0,
    last3_over_rate: 50.0,
    last5_referee_over_rate: 50.0,
    home_aggression_trend: 50.0,
    away_aggression_trend: 50.0,
    odds_over: 1.85,
    odds_under: 1.85
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const value = e.target.type === 'number' ? parseFloat(e.target.value) : e.target.value;
    setFormData({ ...formData, [e.target.name]: value });
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await predictCards(formData);
      setResult(res);
    } catch (error) {
      console.error("Error fetching prediction", error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    if (!result || !result.algorithm_log) return;
    
    const { home_team, away_team } = formData;
    const home = home_team || 'Casa';
    const away = away_team || 'Fora';
    const log = result.algorithm_log;
    
    const content = `=== RELATÓRIO DE ANÁLISE QUANTITATIVA Card Pro ===
Data: ${new Date().toLocaleString()}

[1] DADOS DA PARTIDA E TENDÊNCIAS
----------------------------------------
Partida: ${home} vs ${away}
Médias de Cartões: ${formData.home_cards_avg} (C) / ${formData.away_cards_avg} (F) / ${formData.referee_avg} (Árbitro)
Tendências de Agressividade: ${formData.home_aggression_trend}% (C) / ${formData.away_aggression_trend}% (F)
Over Rate (Últimos Jogos): ${formData.last3_over_rate}% (Geral) / ${formData.last5_referee_over_rate}% (Árbitro)
Odds da Linha 4.5: Over ${formData.odds_over} / Under ${formData.odds_under}

[2] RESULTADO DA PREVISÃO HÍBRIDA
----------------------------------------
Previsão Sugerida (Linha Principal): ${result.prediction.replace('OVER', 'MAIS DE').replace('UNDER', 'MENOS DE')}
Confiança Calibrada: ${result.confidence.toFixed(1)}%
Risk Score: ${result.risk_score ? result.risk_score.toFixed(1) : '0.0'}
Cartões Esperados Exatos (XGBRegressor): ${result.expected_cards}

Probabilidade MAIS DE (Over 4.5): ${result.over_probability.toFixed(1)}% | EV: ${result.ev_over ? result.ev_over.toFixed(2) : 'N/A'}
Probabilidade MENOS DE (Under 4.5): ${result.under_probability.toFixed(1)}% | EV: ${result.ev_under ? result.ev_under.toFixed(2) : 'N/A'}
Edge Score: ${result.edge_score ? result.edge_score.toFixed(1) : 'N/A'}
Classificação de Valor: ${result.value_label || 'N/A'}

[3] MATRIZ DE DISTRIBUIÇÃO POISSON (MULTI-LINHAS)
----------------------------------------
- Linha 4.5: Over ${result.multi_lines?.['4.5']?.over?.toFixed(1)}% / Under ${result.multi_lines?.['4.5']?.under?.toFixed(1)}%
- Linha 5.5: Over ${result.multi_lines?.['5.5']?.over?.toFixed(1)}% / Under ${result.multi_lines?.['5.5']?.under?.toFixed(1)}%
- Linha 6.5: Over ${result.multi_lines?.['6.5']?.over?.toFixed(1)}% / Under ${result.multi_lines?.['6.5']?.under?.toFixed(1)}%

${result.inconsistency_alert ? `\n[!] ALERTA DE CONSISTÊNCIA MATEMÁTICA:\n${result.inconsistency_alert}\n` : ''}
Recomendação da IA:
${result.explanation}

[4] LOGS INTERNOS DO MOTOR
----------------------------------------
Arquitetura do Modelo: ${log.model_type}
Impacto Numérico do Árbitro Calculado: ${log.referee_impact?.toFixed(2) || 'N/A'}
Edge Score Bruto: ${log.edge_score?.toFixed(2) || 'N/A'}

[Fim do Relatório Gerado por Card Pro]
`;
    
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `analise_${home}_vs_${away}.txt`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header className="mb-8">
        <h2 className="text-3xl font-bold tracking-tight">Terminal de Análise de Partida</h2>
        <p className="text-gray-400 mt-2">Insira os dados quantitativos da partida para gerar uma previsão da IA.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Input Form */}
        <div className="lg:col-span-5">
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-6 flex items-center text-gray-200">
              <Target className="mr-2 text-neon-green" size={20} />
              Parâmetros de Entrada
            </h3>
            
            <form onSubmit={handleAnalyze} className="space-y-5">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Nome do Time (Casa)</label>
                  <input type="text" placeholder="Ex: Flamengo" name="home_team" value={formData.home_team} onChange={handleChange} className="w-full bg-gray-950 border border-gray-700 rounded p-2.5 text-white focus:border-neon-green focus:outline-none transition-colors" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Nome do Time (Fora)</label>
                  <input type="text" placeholder="Ex: Palmeiras" name="away_team" value={formData.away_team} onChange={handleChange} className="w-full bg-gray-950 border border-gray-700 rounded p-2.5 text-white focus:border-neon-green focus:outline-none transition-colors" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Média de Cartões - Casa</label>
                  <input type="number" step="0.1" name="home_cards_avg" value={formData.home_cards_avg} onChange={handleChange} className="w-full bg-gray-950 border border-gray-700 rounded p-2.5 text-white focus:border-neon-green focus:outline-none transition-colors" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Média de Cartões - Fora</label>
                  <input type="number" step="0.1" name="away_cards_avg" value={formData.away_cards_avg} onChange={handleChange} className="w-full bg-gray-950 border border-gray-700 rounded p-2.5 text-white focus:border-neon-green focus:outline-none transition-colors" />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Média de Cartões - Árbitro</label>
                <input type="number" step="0.1" name="referee_avg" value={formData.referee_avg} onChange={handleChange} className="w-full bg-gray-950 border border-gray-700 rounded p-2.5 text-white focus:border-neon-green focus:outline-none transition-colors" />
              </div>

              <div className="border-t border-gray-800 pt-4 mt-2">
                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">Tendências Recentes (%)</h4>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-400 mb-2">Over Rate (Últimos 3)</label>
                    <input type="number" step="0.1" name="last3_over_rate" value={formData.last3_over_rate} onChange={handleChange} className="w-full bg-gray-950 border border-gray-700 rounded p-2 text-sm text-white focus:border-neon-green focus:outline-none" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-400 mb-2">Over Rate Árbitro (Últimos 5)</label>
                    <input type="number" step="0.1" name="last5_referee_over_rate" value={formData.last5_referee_over_rate} onChange={handleChange} className="w-full bg-gray-950 border border-gray-700 rounded p-2 text-sm text-white focus:border-neon-green focus:outline-none" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-400 mb-2">Agressividade Casa</label>
                    <input type="number" step="0.1" name="home_aggression_trend" value={formData.home_aggression_trend} onChange={handleChange} className="w-full bg-gray-950 border border-gray-700 rounded p-2 text-sm text-white focus:border-neon-green focus:outline-none" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-400 mb-2">Agressividade Fora</label>
                    <input type="number" step="0.1" name="away_aggression_trend" value={formData.away_aggression_trend} onChange={handleChange} className="w-full bg-gray-950 border border-gray-700 rounded p-2 text-sm text-white focus:border-neon-green focus:outline-none" />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Odds Mais de 4.5</label>
                  <input type="number" step="0.01" name="odds_over" value={formData.odds_over} onChange={handleChange} className="w-full bg-gray-950 border border-gray-700 rounded p-2.5 text-white focus:border-neon-green focus:outline-none transition-colors" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Odds Menos de 4.5</label>
                  <input type="number" step="0.01" name="odds_under" value={formData.odds_under} onChange={handleChange} className="w-full bg-gray-950 border border-gray-700 rounded p-2.5 text-white focus:border-neon-green focus:outline-none transition-colors" />
                </div>
              </div>

              <button 
                type="submit" 
                disabled={loading}
                className="w-full mt-6 bg-neon-green/10 text-neon-green border border-neon-green hover:bg-neon-green hover:text-black font-bold py-3 rounded transition-all duration-300 flex justify-center items-center group"
              >
                {loading ? (
                  <span className="animate-pulse">Processando...</span>
                ) : (
                  <>
                    <Zap className="mr-2" size={18} />
                    Executar Análise
                    <ChevronRight className="ml-2 opacity-0 group-hover:opacity-100 transition-opacity" size={18} />
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-7">
          <AnimatePresence mode="wait">
            {!result ? (
              <motion.div 
                initial={{ opacity: 0 }} 
                animate={{ opacity: 1 }} 
                exit={{ opacity: 0 }}
                className="glass-card h-full flex flex-col items-center justify-center p-12 text-center text-gray-500 border-dashed border-2"
              >
                <AlertTriangle size={48} className="mb-4 opacity-50 text-gray-400" />
                <p>Aguardando dados da partida para calcular a previsão.</p>
              </motion.div>
            ) : (
              <motion.div 
                initial={{ opacity: 0, y: 20 }} 
                animate={{ opacity: 1, y: 0 }} 
                className="glass-card overflow-hidden neon-border"
              >
                {/* Result Header */}
                <div className="bg-gray-950 p-6 border-b border-gray-800 flex justify-between items-center">
                  <div>
                    <p className="text-sm text-gray-400 uppercase tracking-widest font-bold">Previsão Sugerida</p>
                    <h2 className="text-4xl font-black mt-1 neon-text">{result.prediction.replace('OVER', 'MAIS DE').replace('UNDER', 'MENOS DE')}</h2>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-400 uppercase tracking-widest font-bold">Confiança</p>
                    <div className="text-3xl font-black text-white mt-1">
                      {result.confidence.toFixed(1)}<span className="text-lg text-neon-green">%</span>
                    </div>
                  </div>
                </div>

                {/* Body Content */}
                <div className="p-6 space-y-6">
                  <div>
                    <h4 className="text-xs text-gray-500 uppercase tracking-widest font-bold mb-3">Matriz de Probabilidade</h4>
                    <div className="flex h-4 rounded-full overflow-hidden bg-gray-800 w-full mb-2">
                      <div className="bg-neon-green" style={{ width: `${result.over_probability}%` }}></div>
                      <div className="bg-red-500" style={{ width: `${result.under_probability}%` }}></div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-400 font-medium">
                      <span>Mais de: {result.over_probability.toFixed(1)}%</span>
                      <span>Menos de: {result.under_probability.toFixed(1)}%</span>
                    </div>
                  </div>

                  {result.inconsistency_alert && (
                    <div className="bg-red-900/30 border border-red-500/50 p-4 rounded mb-4 flex items-start gap-3">
                      <AlertTriangle className="text-red-400 mt-0.5 shrink-0" size={20} />
                      <div>
                        <h4 className="text-red-400 font-bold text-sm mb-1">LOW MATHEMATICAL CONSISTENCY</h4>
                        <p className="text-red-300 text-xs leading-relaxed">{result.inconsistency_alert.replace("LOW MATHEMATICAL CONSISTENCY: ", "")}</p>
                      </div>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-900/50 p-4 rounded border border-gray-800">
                      <p className="text-xs text-gray-500 uppercase tracking-widest mb-1">Cartões Esperados</p>
                      <p className="text-xl font-bold text-gray-200">{result.expected_cards}</p>
                    </div>
                    <div className="bg-gray-900/50 p-4 rounded border border-gray-800">
                      <p className="text-xs text-gray-500 uppercase tracking-widest mb-1">Risk Score</p>
                      <p className="text-xl font-bold text-gray-200 flex items-center gap-2">
                        {result.risk_score ? result.risk_score.toFixed(1) : '0.0'}
                        <Activity className={result.risk_score > 60 ? 'text-red-500' : 'text-neon-green'} size={16} />
                      </p>
                    </div>
                  </div>

                  {result.value_label && (
                    <div className="bg-neon-green/10 border border-neon-green p-4 rounded text-center">
                      <p className="text-xs text-neon-green uppercase tracking-widest font-bold mb-1">Classificação de Valor</p>
                      <p className="text-xl font-black text-white">{result.value_label}</p>
                      <p className="text-xs text-gray-400 mt-1">Edge Score: {result.edge_score ? result.edge_score.toFixed(1) : '0.0'}</p>
                    </div>
                  )}

                  {result.multi_lines && (
                    <div className="bg-gray-900/50 p-4 rounded border border-gray-800">
                      <p className="text-xs text-gray-500 uppercase tracking-widest font-bold mb-3">Previsão Multi-Linhas (Poisson)</p>
                      <div className="space-y-3">
                        {['4.5', '5.5', '6.5'].map(line => (
                          <div key={line} className="flex items-center justify-between text-sm">
                            <span className="font-bold text-gray-300">Linha {line}</span>
                            <div className="flex gap-4">
                              <span className="text-neon-green">Over: {result.multi_lines[line]?.over?.toFixed(1)}%</span>
                              <span className="text-red-400">Under: {result.multi_lines[line]?.under?.toFixed(1)}%</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="bg-gray-900/50 p-4 rounded border border-gray-800 mt-4">
                    <p className="text-xs text-gray-500 uppercase tracking-widest mb-1">Recomendação da IA</p>
                    <p className="text-sm text-gray-300 leading-relaxed">{result.explanation}</p>
                  </div>
                  
                  {result.algorithm_log && (
                    <button onClick={handleExport} className="w-full mt-4 bg-gray-800 hover:bg-gray-700 text-white font-bold py-3 rounded transition-colors flex justify-center items-center">
                      <Download className="mr-2" size={18} />
                      Exportar Detalhes da Análise (.txt)
                    </button>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
