import React, { useState, useEffect, useRef } from 'react';
import { Activity, Radio, Sun, Thermometer, Wind, Zap } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import './App.css';

// ============================================================================
// 📊 CENTRAL AUDIO CONFIGURATION DECK
// Dropping leading slashes allows the browser to resolve paths correctly in containers
// ============================================================================
const AUDIO_CONFIG = {
  buttonClick: "click.wav",
  buttonHover: "button-hover.wav",
  graphHover:  null,
  alarmSiren:  "alarm.wav"
};

const generateInitialSeedData = () => {
  const seed = [];
  const now = new Date();
  for (let i = 40; i > 0; i--) {
    const historicalTime = new Date(now.getTime() - i * 1000);
    seed.push({
      step_index: 40 - i + 1,
      time_label: historicalTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      oxygen: 21.04,
      pressure: 101.32,
      temperature: 22.15,
      vibration: 0.021,
      solar_flux: 453,
      transformer_loss: 0.0
    });
  }
  return seed;
};

export default function App() {
  const [anomalyMatrix, setAnomalyMatrix] = useState({});
  const [chartData, setChartData] = useState(() => generateInitialSeedData());
  const [aiAlarmActive, setAiAlarmActive] = useState(false);     
  const [liveMetrics, setLiveMetrics] = useState({
    oxygen: 21.04,
    pressure: 101.32,
    temperature: 22.15,
    vibration: 0.021,
    solar_flux: 453,
    transformer_loss: 0.0,
    accumulated_damage: 0.0
  });
  const [visualDamage, setVisualDamage] = useState(0);
  const socketRef = useRef(null);
  const latestDataRef = useRef(null);
  const lastActiveIndexRef = useRef(null);
  
  const clickAudioRef = useRef(null);
  const hoverAudioRef = useRef(null);
  const graphAudioRef = useRef(null);
  const alarmAudioRef = useRef(null);
  const STATIC_TICKS = [1, 10, 20, 30, 40];

  // --- ONE-TIME RUNTIME INSTANTIATION ENGINE ---
  useEffect(() => {
    clickAudioRef.current = new Audio(AUDIO_CONFIG.buttonClick);
    hoverAudioRef.current = new Audio(AUDIO_CONFIG.buttonHover);
    graphAudioRef.current = new Audio(AUDIO_CONFIG.graphHover);
    alarmAudioRef.current = new Audio(AUDIO_CONFIG.alarmSiren);
    
    clickAudioRef.current.load();
    hoverAudioRef.current.load();
    graphAudioRef.current.load();
    alarmAudioRef.current.load();
    
    return () => {
      if (alarmAudioRef.current) alarmAudioRef.current.pause();
    };
  }, []);

  // --- AUDIO EXECUTION HANDLERS ---
  const playClickChime = () => {
    if (!clickAudioRef.current) return;
    clickAudioRef.current.currentTime = 0;
    clickAudioRef.current.volume = 0.25; 
    clickAudioRef.current.play().catch(() => {});
  };

  const playHoverChime = () => {
    if (!hoverAudioRef.current) return;
    hoverAudioRef.current.currentTime = 0;
    hoverAudioRef.current.volume = 0.10; 
    hoverAudioRef.current.play().catch(() => {});
  };

  const playGraphTick = () => {
    if (!graphAudioRef.current) return;
    graphAudioRef.current.currentTime = 0;
    graphAudioRef.current.volume = 0.15; 
    graphAudioRef.current.play().catch(() => {});
  };

  const handleChartMouseMove = (state) => {
    if (state && state.activeTooltipIndex !== undefined) {
      if (state.activeTooltipIndex !== lastActiveIndexRef.current) {
        lastActiveIndexRef.current = state.activeTooltipIndex;
        playGraphTick();
      }
    }
  };

  // Synchronize Master Warning Siren with Neural Network loss metrics
  useEffect(() => {
    if (!alarmAudioRef.current) return;
        
    if (aiAlarmActive) {
      alarmAudioRef.current.loop = true;
      alarmAudioRef.current.volume = 0.20;
      alarmAudioRef.current.play().catch(() => {});
    } else {
      alarmAudioRef.current.pause();
      alarmAudioRef.current.currentTime = 0;
    }
  }, [aiAlarmActive]);

  // --- DYNAMIC PRODUCTION WEBSOCKET ENGINE ---
  useEffect(() => {
    // Dynamically calculate the browser's origin protocol and host location
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const socketUrl = `${protocol}//${window.location.host}/ws`;
    
    console.log(`📡 Connecting frontend pipeline to target vector: ${socketUrl}`);
    socketRef.current = new WebSocket(socketUrl);

    socketRef.current.onmessage = (event) => {
      latestDataRef.current = JSON.parse(event.data);
    };

    socketRef.current.onerror = (err) => {
      console.error("❌ WebSocket error caught: ", err);
    };

    const uiRenderInterval = setInterval(() => {
      if (!latestDataRef.current) return;
            
      const currentPayload = latestDataRef.current;
      const isModelAnomalous = currentPayload.transformer_loss > 0.0;
      setAiAlarmActive(isModelAnomalous);
            
      setLiveMetrics(currentPayload);
      setAnomalyMatrix(currentPayload.active_matrix || {});
      setChartData((prev) => {
        const next = [...prev, {
          step_index: prev.length + 1, 
          time_label: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
          oxygen: currentPayload.oxygen,
          pressure: currentPayload.pressure,
          temperature: currentPayload.temperature,
          vibration: currentPayload.vibration,
          solar_flux: currentPayload.solar_flux,
          transformer_loss: currentPayload.transformer_loss
        }];
                
        if (next.length > 40) next.shift(); 
        return next.map((item, index) => ({
          ...item,
          step_index: index + 1
        }));
      });
    }, 200); 

    return () => {
      if (socketRef.current) socketRef.current.close();
      clearInterval(uiRenderInterval);
    };
  }, []);

  useEffect(() => {
    const smoothingTicker = setInterval(() => {
      setVisualDamage((prev) => {
        const target = liveMetrics.accumulated_damage;
        return prev + (target - prev) * 0.08; 
      });
    }, 30); 
    return () => clearInterval(smoothingTicker);
  }, [liveMetrics.accumulated_damage]);

  const triggerSimulation = (cmdString) => {
    playClickChime();
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ command: cmdString }));
    }
  };

  const calculateIntegrityPercent = () => {
    const rawScore = 100 - (visualDamage * 180);
    return Math.max(14, Math.floor(rawScore));
  };

  const isO2Anomaly       = aiAlarmActive && (anomalyMatrix.o2_rise || anomalyMatrix.o2_fall);
  const isPressureAnomaly = aiAlarmActive && (anomalyMatrix.press_rise || anomalyMatrix.press_fall);
  const isTempAnomaly     = aiAlarmActive && (anomalyMatrix.temp_rise || anomalyMatrix.temp_fall);
  const isVibeAnomaly     = aiAlarmActive && anomalyMatrix.vibration;
  const isSolarAnomaly    = aiAlarmActive && anomalyMatrix.solar;

  const renderTooltipFormatter = (value, name) => [value, name.toUpperCase()];
  const renderTooltipLabelFormatter = (label) => {
    const point = chartData.find(d => d.step_index === label);
    return point ? `System Time: ${point.time_label}` : `Index Step: ${label}`;
  };
  const formatXAxisTicks = (tick) => {
    const match = chartData.find(d => d.step_index === tick);
    return match ? match.time_label : `T-${40 - tick}s`;
  };

  return (
    <div className="dashboard-container">
      <div className="command-deck-header">
        <div className="telemetry-rod left-rod">
          <div className={`rod-metric-field ${isO2Anomaly ? 'neon-red-text' : ''}`}>
            <span className="rod-label">O2 CONCENTRATION</span>
            <span className="rod-value">{liveMetrics.oxygen} %</span>
          </div>
          <div className={`rod-metric-field ${isPressureAnomaly ? 'neon-red-text' : ''}`}>
            <span className="rod-label">CABIN PRESSURE</span>
            <span className="rod-value">{liveMetrics.pressure} kPa</span>
          </div>
          <div className={`rod-metric-field ${isTempAnomaly ? 'neon-red-text' : ''}`}>
            <span className="rod-label">CORE TEMPERATURE</span>
            <span className="rod-value">{liveMetrics.temperature} °C</span>
          </div>
        </div>
        
        <div className="sphere-suspension-zone">
          {aiAlarmActive && (
            <>
              <div className="sphere-wave wave-layer-1" />
              <div className="sphere-wave wave-layer-2" />
            </>
          )}
          <div className={`floating-ai-sphere ${aiAlarmActive ? 'sphere-panic-mode' : ''}`}>
            <span className="sphere-percentage">{calculateIntegrityPercent()}%</span>
            <span className="sphere-subtext">{aiAlarmActive ? 'ANOMALY DETECTED' : 'INTEGRITY'}</span>
          </div>
        </div>

        <div className="telemetry-rod right-rod">
          <div className={`rod-metric-field ${isVibeAnomaly ? 'neon-red-text' : ''}`}>
            <span className="rod-label">STRUCTURAL VIBE</span>
            <span className="rod-value">{liveMetrics.vibration} Hz</span>
          </div>
          <div className={`rod-metric-field ${isSolarAnomaly ? 'neon-red-text' : ''}`}>
            <span className="rod-label">SOLAR RADIATION</span>
            <span className="rod-value">{liveMetrics.solar_flux} W/m²</span>
          </div>
          <div className="rod-metric-field">
            <span className="rod-label">COGNITIVE STATUS</span>
            <span className={`rod-value status-tag ${aiAlarmActive ? 'panic-status' : 'nominal-status'}`}>
              {aiAlarmActive ? 'DEGRADED' : 'NOMINAL'}
            </span>
          </div>
        </div>
      </div>

      <div className="system-banner-title">Lunar Capsule Digital Twin Matrix</div>
      <div className="charts-grid-matrix">
        {/* CARD 1: OXYGEN */}
        <div className={`chart-card-box ${isO2Anomaly ? 'card-fracture-red' : ''}`}>
          <div className="chart-card-title-row">
            <Wind className="chart-icon" /> <span>OXYGEN CONCENTRATION PROFILE</span>
          </div>
          <div className="chart-render-viewport">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} onMouseMove={handleChartMouseMove} margin={{ top: 5, right: 15, left: -20, bottom: 5 }}>
                <CartesianGrid stroke="#121b2d" strokeDasharray="3 3" />
                <XAxis dataKey="step_index" ticks={STATIC_TICKS} type="number" domain={[1, 40]} tickFormatter={formatXAxisTicks} tick={{ fontSize: 9, fill: '#64748b' }} />
                <YAxis stroke="#334155" tick={{ fontSize: 9 }} domain={[10, 35]} />
                <Tooltip formatter={renderTooltipFormatter} labelFormatter={renderTooltipLabelFormatter} contentStyle={{ backgroundColor: '#090f1c', borderColor: '#1e293b', fontSize: 11 }} />
                <Line type="monotone" dataKey="oxygen" stroke={isO2Anomaly ? '#ef4444' : '#22d3ee'} strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="chart-footer-controls">
            <button className="footer-btn btn-action" onMouseEnter={playHoverChime} onClick={() => triggerSimulation('o2_rise')}>Rise</button>
            <button className="footer-btn btn-action" onMouseEnter={playHoverChime} onClick={() => triggerSimulation('o2_fall')}>Leak</button>
            <button className="footer-btn btn-clear" onMouseEnter={playHoverChime} onClick={() => { triggerSimulation('clear_o2_rise'); triggerSimulation('clear_o2_fall'); }}>Reset</button>
          </div>
        </div>

        {/* CARD 2: CABIN PRESSURE */}
        <div className={`chart-card-box ${isPressureAnomaly ? 'card-fracture-red' : ''}`}>
          <div className="chart-card-title-row">
            <Radio className="chart-icon" /> <span>CABIN ATMOSPHERIC PRESSURE</span>
          </div>
          <div className="chart-render-viewport">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} onMouseMove={handleChartMouseMove} margin={{ top: 5, right: 15, left: -20, bottom: 5 }}>
                <CartesianGrid stroke="#121b2d" strokeDasharray="3 3" />
                <XAxis dataKey="step_index" ticks={STATIC_TICKS} type="number" domain={[1, 40]} tickFormatter={formatXAxisTicks} tick={{ fontSize: 9, fill: '#64748b' }} />
                <YAxis stroke="#334155" tick={{ fontSize: 9 }} domain={[65, 135]} />
                <Tooltip formatter={renderTooltipFormatter} labelFormatter={renderTooltipLabelFormatter} contentStyle={{ backgroundColor: '#090f1c', borderColor: '#1e293b', fontSize: 11 }} />
                <Line type="monotone" dataKey="pressure" stroke={isPressureAnomaly ? '#ef4444' : '#22d3ee'} strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>            </ResponsiveContainer>
          </div>
          <div className="chart-footer-controls">
            <button className="footer-btn btn-action" onMouseEnter={playHoverChime} onClick={() => triggerSimulation('press_rise')}>Surge</button>
            <button className="footer-btn btn-action" onMouseEnter={playHoverChime} onClick={() => triggerSimulation('press_fall')}>Drop</button>
            <button className="footer-btn btn-clear" onMouseEnter={playHoverChime} onClick={() => { triggerSimulation('clear_press_rise'); triggerSimulation('clear_press_fall'); }}>Reset</button>
          </div>
        </div>

        {/* CARD 3: TEMPERATURE */}
        <div className={`chart-card-box ${isTempAnomaly ? 'card-fracture-red' : ''}`}>
          <div className="chart-card-title-row">
            <Thermometer className="chart-icon" /> <span>THERMAL VECTOR CORE TRENDS</span>
          </div>
          <div className="chart-render-viewport">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} onMouseMove={handleChartMouseMove} margin={{ top: 5, right: 15, left: -20, bottom: 5 }}>
                <CartesianGrid stroke="#121b2d" strokeDasharray="3 3" />
                <XAxis dataKey="step_index" ticks={STATIC_TICKS} type="number" domain={[1, 40]} tickFormatter={formatXAxisTicks} tick={{ fontSize: 9, fill: '#64748b' }} />
                <YAxis stroke="#334155" tick={{ fontSize: 9 }} domain={[0, 50]} />
                <Tooltip formatter={renderTooltipFormatter} labelFormatter={renderTooltipLabelFormatter} contentStyle={{ backgroundColor: '#090f1c', borderColor: '#1e293b', fontSize: 11 }} />
                <Line type="monotone" dataKey="temperature" stroke={isTempAnomaly ? '#ef4444' : '#22d3ee'} strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="chart-footer-controls">
            <button className="footer-btn btn-action" onMouseEnter={playHoverChime} onClick={() => triggerSimulation('temp_rise')}>Rise</button>
            <button className="footer-btn btn-action" onMouseEnter={playHoverChime} onClick={() => triggerSimulation('temp_fall')}>Fall</button>
            <button className="footer-btn btn-clear" onMouseEnter={playHoverChime} onClick={() => { triggerSimulation('clear_temp_rise'); triggerSimulation('clear_temp_fall'); }}>Reset</button>
          </div>
        </div>

        {/* CARD 4: VIBRATION */}
        <div className={`chart-card-box ${isVibeAnomaly ? 'card-fracture-red' : ''}`}>
          <div className="chart-card-title-row">
            <Zap className="chart-icon" /> <span>STRUCTURAL VIBRATION FREQUENCY</span>
          </div>
          <div className="chart-render-viewport">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} onMouseMove={handleChartMouseMove} margin={{ top: 5, right: 15, left: -20, bottom: 5 }}>
                <CartesianGrid stroke="#121b2d" strokeDasharray="3 3" />
                <XAxis dataKey="step_index" ticks={STATIC_TICKS} type="number" domain={[1, 40]} tickFormatter={formatXAxisTicks} tick={{ fontSize: 9, fill: '#64748b' }} />
                <YAxis stroke="#334155" tick={{ fontSize: 9 }} domain={[0, 0.3]} />
                <Tooltip formatter={renderTooltipFormatter} labelFormatter={renderTooltipLabelFormatter} contentStyle={{ backgroundColor: '#090f1c', borderColor: '#1e293b', fontSize: 11 }} />
                <Line type="monotone" dataKey="vibration" stroke={isVibeAnomaly ? '#ef4444' : '#22d3ee'} strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="chart-footer-controls">
            <button className="footer-btn btn-action" onMouseEnter={playHoverChime} onClick={() => triggerSimulation('vibration')}>Spike HZ</button>
            <button className="footer-btn btn-clear" onMouseEnter={playHoverChime} onClick={() => triggerSimulation('clear_vibration')}>Reset</button>
          </div>
        </div>

        {/* CARD 5: SOLAR RADIATION */}
        <div className={`chart-card-box ${isSolarAnomaly ? 'card-fracture-red' : ''}`}>
          <div className="chart-card-title-row">
            <Sun className="chart-icon" /> <span>SOLAR MATRIX RADIATION INTENSITY</span>
          </div>
          <div className="chart-render-viewport">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} onMouseMove={handleChartMouseMove} margin={{ top: 5, right: 15, left: -20, bottom: 5 }}>
                <CartesianGrid stroke="#121b2d" strokeDasharray="3 3" />
                <XAxis dataKey="step_index" ticks={STATIC_TICKS} type="number" domain={[1, 40]} tickFormatter={formatXAxisTicks} tick={{ fontSize: 9, fill: '#64748b' }} />
                <YAxis stroke="#334155" tick={{ fontSize: 9 }} domain={[350, 1050]} />
                <Tooltip formatter={renderTooltipFormatter} labelFormatter={renderTooltipLabelFormatter} contentStyle={{ backgroundColor: '#090f1c', borderColor: '#1e293b', fontSize: 11 }} />
                <Line type="monotone" dataKey="solar_flux" stroke={isSolarAnomaly ? '#ef4444' : '#22d3ee'} strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="chart-footer-controls">
            <button className="footer-btn btn-action" onMouseEnter={playHoverChime} onClick={() => triggerSimulation('solar')}>Flux Spike</button>
            <button className="footer-btn btn-clear" onMouseEnter={playHoverChime} onClick={() => { triggerSimulation('clear_solar'); }}>Reset</button>
          </div>
        </div>

        {/* CARD 6: MASTER OVERLAY SPECTRUM */}
        <div className={`chart-card-box ${aiAlarmActive ? 'card-fracture-red' : ''}`}>
          <div className="chart-card-title-row">
            <Activity className="chart-icon" /> <span>MASTER DATA OVERLAY SPECTRUM</span>
          </div>
          <div className="chart-render-viewport">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} onMouseMove={handleChartMouseMove} margin={{ top: 5, right: 15, left: -20, bottom: 5 }}>
                <CartesianGrid stroke="#121b2d" strokeDasharray="3 3" />
                <XAxis dataKey="step_index" ticks={STATIC_TICKS} type="number" domain={[1, 40]} tickFormatter={formatXAxisTicks} tick={{ fontSize: 9, fill: '#64748b' }} />
                <YAxis stroke="#334155" tick={{ fontSize: 9 }} />
                <Tooltip formatter={renderTooltipFormatter} labelFormatter={renderTooltipLabelFormatter} contentStyle={{ backgroundColor: '#090f1c', borderColor: '#1e293b', fontSize: 11 }} />
                                
                <Line type="monotone" dataKey="pressure" stroke="#22d3ee" strokeWidth={1.5} dot={false} name="Pressure" isAnimationActive={false} />
                <Line type="monotone" dataKey="oxygen" stroke="#a855f7" strokeWidth={1.5} dot={false} name="Oxygen" isAnimationActive={false} />
                <Line type="monotone" dataKey="temperature" stroke="#eab308" strokeWidth={1.5} dot={false} name="Temperature" isAnimationActive={false} />
                <Line type="monotone" dataKey="vibration" stroke="#ec4899" strokeWidth={1.5} dot={false} name="Vibration" isAnimationActive={false} />
                <Line type="monotone" dataKey="solar_flux" stroke="#10b981" strokeWidth={1.5} dot={false} name="Solar" isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="chart-footer-controls">
            <button className="footer-btn btn-clear" onMouseEnter={playHoverChime} style={{ width: '100%' }} onClick={() => triggerSimulation('nominal')}>
              Flush All System Faults
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
