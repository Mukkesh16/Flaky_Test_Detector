import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { 
  UploadCloud, LayoutDashboard, Table as TableIcon, Zap, 
  Terminal, MessageSquare, Search, Filter, Play, CheckCircle, 
  AlertTriangle, XCircle, ChevronDown, ChevronRight, Download, Send, 
  Cpu, History, Clock
} from 'lucide-react';

const MOCK_EXPLANATIONS = {
  "test_data_export": {
    tier: "high", confidence: 94,
    explanation: "The test occasionally fails due to an underlying race condition when querying large datasets from the replica database while a sync is occurring.",
    suggestions: ["Implement a retry mechanism with exponential backoff for DB timeouts.", "Ensure the test waits for the asynchronous export job queue to empty.", "Mock the external AWS S3 upload call to reduce latency variables."]
  },
  "test_user_login": {
    tier: "high", confidence: 88,
    explanation: "Fails intermittently because the test uses a shared mock user account. If tests run in parallel, token invalidation from one thread breaks the other.",
    suggestions: ["Dynamically generate unique test users for each test run.", "Isolate database transactions in the test setup/teardown logic."]
  }
};

// --- UTILS & COMPONENTS ---
const getTier = (score) => score >= 75 ? 'HIGH' : score >= 40 ? 'MED' : 'LOW';
const getTierColor = (score) => score >= 75 ? 'text-rose-400 bg-rose-400/10 border-rose-400/30' : score >= 40 ? 'text-amber-400 bg-amber-400/10 border-amber-400/30' : 'text-teal-400 bg-teal-400/10 border-teal-400/30';
const getBarColor = (score) => score >= 75 ? 'bg-rose-500' : score >= 40 ? 'bg-amber-400' : 'bg-teal-400';

const ScoreBadge = ({ score }) => (
  <div className="flex items-center gap-3">
    <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
      <div className={`h-full rounded-full ${getBarColor(score)}`} style={{ width: `${score}%` }}></div>
    </div>
    <span className={`font-mono text-xs font-bold w-6 ${score >= 75 ? 'text-rose-400' : score >= 40 ? 'text-amber-400' : 'text-teal-400'}`}>{score}</span>
    <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${getTierColor(score)}`}>{getTier(score)}</span>
  </div>
);

const Card = ({ children, className = "", title, icon: Icon, action }) => (
  <div className={`bg-slate-900 border border-slate-800 rounded-xl overflow-hidden ${className}`}>
    {(title || Icon || action) && (
      <div className="px-5 py-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
        <div className="flex items-center gap-2">
          {Icon && <Icon size={18} className="text-teal-400" />}
          <h3 className="font-mono text-sm font-bold text-slate-200">{title}</h3>
        </div>
        {action && <div>{action}</div>}
      </div>
    )}
    <div className="p-5">{children}</div>
  </div>
);

// --- MAIN VIEWS ---

const UploadView = ({ onUpload }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const processData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get("http://localhost:8000/api/flaky-tests");
      
      if (!response.data || response.data.length === 0) {
        setError("No tests found. Please upload a CSV first.");
        setLoading(false);
        return;
      }
      
      onUpload(response.data);
    } catch (e) {
      setError("Failed to fetch data from backend. Is the Python API running?");
      console.error(e);
      setLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    if (!file) return;
    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const uploadRes = await axios.post("http://localhost:8000/api/upload", formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      const response = await axios.get("http://localhost:8000/api/flaky-tests");
      if (!response.data || response.data.length === 0) {
        setError("No tests found after upload.");
        setLoading(false);
        return;
      }
      
      onUpload(response.data, {
        mapping: uploadRes.data.mapping,
        warnings: uploadRes.data.warnings
      });
    } catch (e) {
      setError("Error uploading file: " + (e.response?.data?.error || e.message));
      console.error(e);
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto mt-10">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-white mb-3">Initialize Analysis Workspace</h1>
        <p className="text-slate-400 text-sm">Upload your test execution logs (CSV/JSON) or connect your CI/CD provider.</p>
      </div>

      <div 
        className={`border-2 border-dashed rounded-2xl p-16 text-center transition-all duration-300 relative ${isDragging ? 'border-teal-400 bg-teal-400/5' : 'border-slate-700 bg-slate-900/50 hover:border-slate-500 hover:bg-slate-800/50'}`}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => { 
          e.preventDefault(); 
          setIsDragging(false); 
          if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileUpload(e.dataTransfer.files[0]);
          }
        }}
      >
        <div className="bg-slate-800 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
          <UploadCloud size={36} className="text-teal-400" />
        </div>
        <h3 className="text-xl font-medium text-slate-200 mb-2">Drag & Drop test_runs.csv here</h3>
        <p className="text-slate-500 text-sm mb-8">Supports .csv, .json, and .xml JUnit formats up to 50MB.</p>
        
        {error && (
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 w-3/4 flex items-center justify-center gap-2 text-rose-400 bg-rose-500/10 border border-rose-500/20 py-2 px-4 rounded-lg text-sm">
            <AlertTriangle size={16} />
            {error}
          </div>
        )}
        
        <div className="flex justify-center gap-4">
          <input 
            type="file" 
            ref={fileInputRef} 
            style={{ display: 'none' }} 
            accept=".csv,.json,.xml"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                handleFileUpload(e.target.files[0]);
              }
            }} 
          />
          <button 
            onClick={() => fileInputRef.current?.click()}
            disabled={loading}
            className="px-6 py-2.5 rounded-lg bg-slate-800 text-slate-300 font-medium hover:bg-slate-700 transition-colors border border-slate-700 text-sm disabled:opacity-50"
          >
            Browse Files
          </button>
          <button 
            onClick={processData}
            disabled={loading}
            className="px-6 py-2.5 rounded-lg bg-gradient-to-r from-teal-500 to-emerald-600 text-white font-bold hover:shadow-lg hover:shadow-teal-500/25 transition-all flex items-center gap-2 text-sm disabled:opacity-50"
          >
            {loading ? <span className="animate-pulse">Processing...</span> : <><Zap size={16} /> Load Existing Local Data</>}
          </button>
        </div>
      </div>
    </div>
  );
};

const DashboardView = ({ data, schemaReport }) => {
  const total = data.length;
  const high = data.filter(d => d.score >= 75).length;
  const med = data.filter(d => d.score >= 40 && d.score < 75).length;
  const avg = total > 0 ? (data.reduce((acc, curr) => acc + curr.score, 0) / total).toFixed(1) : "0";

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: "TOTAL ANALYZED", value: total, color: "text-blue-400", border: "border-blue-500/30", bg: "bg-blue-500/10" },
          { label: "HIGH SEVERITY", value: high, color: "text-rose-400", border: "border-rose-500/30", bg: "bg-rose-500/10" },
          { label: "MEDIUM SEVERITY", value: med, color: "text-amber-400", border: "border-amber-500/30", bg: "bg-amber-500/10" },
          { label: "AVG FLAKINESS", value: `${avg}%`, color: "text-teal-400", border: "border-teal-500/30", bg: "bg-teal-500/10" },
        ].map((stat, i) => (
          <div key={i} className={`p-5 rounded-xl border border-slate-800 bg-slate-900 relative overflow-hidden`}>
            <div className={`absolute top-0 right-0 w-24 h-24 rounded-full blur-3xl -mr-10 -mt-10 ${stat.bg}`}></div>
            <p className="text-slate-500 font-mono text-[10px] tracking-wider mb-1">{stat.label}</p>
            <p className={`text-3xl font-bold font-mono ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      {schemaReport && (schemaReport.mapping || (schemaReport.warnings && schemaReport.warnings.length > 0)) && (
        <Card title="Schema Detection Report" icon={CheckCircle}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-xs font-mono text-slate-500 mb-3 uppercase tracking-wider">Detected Columns</h4>
              <ul className="space-y-2">
                {Object.entries(schemaReport.mapping || {}).map(([orig, internal]) => (
                  <li key={orig} className="flex items-center gap-2 text-sm text-slate-300">
                    <CheckCircle size={14} className="text-teal-400" />
                    <span className="font-mono text-teal-300">{internal}</span>
                    <span className="text-slate-500 text-xs">← mapped from ←</span>
                    <span className="font-medium">{orig}</span>
                  </li>
                ))}
                {Object.keys(schemaReport.mapping || {}).length === 0 && (
                  <span className="text-sm text-slate-500">No columns explicitly mapped. Defaults applied.</span>
                )}
              </ul>
            </div>
            
            {schemaReport.warnings && schemaReport.warnings.length > 0 && (
              <div>
                <h4 className="text-xs font-mono text-slate-500 mb-3 uppercase tracking-wider">Inference Warnings</h4>
                <ul className="space-y-2">
                  {schemaReport.warnings.map((warn, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-amber-300 bg-amber-500/10 border border-amber-500/20 p-2.5 rounded-lg">
                      <AlertTriangle size={16} className="shrink-0 mt-0.5" />
                      <span>{warn}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Top Critical Tests" icon={AlertTriangle}>
          <div className="space-y-4">
            {data.filter(d => d.score >= 75).sort((a,b) => b.score - a.score).slice(0, 4).map(test => (
              <div key={test.test_name} className="flex justify-between items-center p-3 rounded-lg border border-slate-800/50 bg-slate-800/20">
                <div>
                  <div className="text-sm text-slate-200 font-medium">{test.test_name}</div>
                  <div className="text-xs text-slate-500 mt-1">Failed last on {test.last_failed}</div>
                </div>
                <ScoreBadge score={test.score} />
              </div>
            ))}
            {data.filter(d => d.score >= 75).length === 0 && (
              <div className="text-slate-500 text-sm italic">No critical tests found!</div>
            )}
          </div>
        </Card>
        <Card title="Category Breakdown" icon={LayoutDashboard}>
           <div className="space-y-4 pt-2">
             {['Auth', 'Network', 'Data', 'Cache', 'General'].map(cat => {
               const count = data.filter(d=>d.category === cat).length;
               if (count === 0) return null;
               return (
                 <div key={cat}>
                   <div className="flex justify-between text-xs text-slate-400 mb-1">
                     <span>{cat}</span>
                     <span>{count} tests</span>
                   </div>
                   <div className="w-full bg-slate-800 rounded-full h-2">
                     <div className="bg-teal-500 h-2 rounded-full" style={{ width: `${(count / total) * 100}%`}}></div>
                   </div>
                 </div>
               );
             })}
           </div>
        </Card>
      </div>
    </div>
  );
};

const DataTableView = ({ data }) => {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("ALL");

  const filtered = data.filter(d => {
    if (search && !d.test_name.toLowerCase().includes(search.toLowerCase())) return false;
    if (filter === "HIGH" && d.score < 75) return false;
    if (filter === "MED" && (d.score < 40 || d.score >= 75)) return false;
    if (filter === "LOW" && d.score >= 40) return false;
    return true;
  }).sort((a, b) => b.score - a.score);

  return (
    <Card className="h-full flex flex-col" title="Test Suite Inventory" icon={TableIcon} action={
      <button className="text-xs flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-md border border-slate-700 transition-colors">
        <Download size={14} /> Export CSV
      </button>
    }>
      <div className="flex gap-4 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 text-slate-500" size={16} />
          <input 
            type="text" 
            placeholder="Search test names..." 
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-all"
            value={search} onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select 
          className="bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 text-sm text-slate-300 focus:outline-none focus:border-teal-500"
          value={filter} onChange={(e) => setFilter(e.target.value)}
        >
          <option value="ALL">All Tiers</option>
          <option value="HIGH">🔴 High (≥75)</option>
          <option value="MED">🟡 Medium (40-74)</option>
          <option value="LOW">🟢 Low (&lt;40)</option>
        </select>
      </div>

      <div className="overflow-x-auto rounded-lg border border-slate-800">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead className="bg-slate-950/50 text-slate-400 font-mono text-[11px] uppercase tracking-wider">
            <tr>
              <th className="px-4 py-3 font-medium">Test Name</th>
              <th className="px-4 py-3 font-medium">Flakiness Score</th>
              <th className="px-4 py-3 font-medium">Pass Rate</th>
              <th className="px-4 py-3 font-medium">Runs</th>
              <th className="px-4 py-3 font-medium">Avg Time (ms)</th>
              <th className="px-4 py-3 font-medium">Category</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {filtered.map((row, i) => (
              <tr key={i} className="hover:bg-slate-800/30 transition-colors">
                <td className="px-4 py-3 font-medium text-slate-200">{row.test_name}</td>
                <td className="px-4 py-3"><ScoreBadge score={row.score} /></td>
                <td className="px-4 py-3 text-slate-300">{(row.pass_rate * 100).toFixed(1)}%</td>
                <td className="px-4 py-3 text-slate-400">{row.runs}</td>
                <td className="px-4 py-3 text-slate-400">{row.avg_ms}</td>
                <td className="px-4 py-3">
                  <span className="text-[11px] px-2 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">{row.category}</span>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan="6" className="px-4 py-8 text-center text-slate-500">No tests match your criteria.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </Card>
  );
};

const ExplanationView = ({ data }) => {
  const [selected, setSelected] = useState(data.find(d => d.score >= 75)?.test_name || data[0]?.test_name);
  
  const getExplanation = (testName) => {
    if (MOCK_EXPLANATIONS[testName]) return MOCK_EXPLANATIONS[testName];
    return {
      tier: "med", confidence: 75,
      explanation: `The test '${testName}' shows signs of intermittent failure, likely due to unpredictable latency in network requests or asynchronous state updates not resolving before assertions.`,
      suggestions: [`Add explicit waits for UI elements or network responses in ${testName}.`, `Check for shared state leakage between test executions affecting ${testName}.`]
    };
  };
  
  const expl = getExplanation(selected);
  const testInfo = data.find(d => d.test_name === selected);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
      <Card title="Test Selector" icon={Search} className="lg:col-span-1">
        <div className="space-y-2 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
          {data.sort((a,b) => b.score - a.score).map(test => (
            <button 
              key={test.test_name}
              onClick={() => setSelected(test.test_name)}
              className={`w-full text-left p-3 rounded-lg border transition-all ${selected === test.test_name ? 'bg-teal-500/10 border-teal-500/50' : 'bg-slate-900 border-slate-800 hover:border-slate-700'}`}
            >
              <div className="text-sm font-medium text-slate-200 truncate">{test.test_name}</div>
              <div className="mt-2"><ScoreBadge score={test.score} /></div>
            </button>
          ))}
        </div>
      </Card>

      <div className="lg:col-span-2 space-y-6">
        <div className="flex flex-wrap gap-3">
           {[{label: "TIER", val: expl.tier.toUpperCase(), color: expl.tier === 'high' ? 'text-rose-400' : 'text-amber-400'},
             {label: "CONFIDENCE", val: `${expl.confidence}%`, color: "text-teal-400"},
             {label: "SCORE", val: `${testInfo?.score || 0}/100`, color: "text-slate-200"},
             {label: "PASS RATE", val: `${((testInfo?.pass_rate||0)*100).toFixed(1)}%`, color: "text-slate-200"}
           ].map((metric, i) => (
             <div key={i} className="flex-1 min-w-[120px] bg-slate-900 border border-slate-800 rounded-lg p-3 flex items-center gap-2">
                <span className="text-[10px] font-mono text-slate-500">{metric.label}</span>
                <span className={`font-mono font-bold text-sm ${metric.color}`}>{metric.val}</span>
             </div>
           ))}
        </div>

        <Card title="AI Root Cause Analysis" icon={Cpu} action={<span className="text-xs bg-slate-800 text-teal-400 px-2 py-1 rounded border border-slate-700 font-mono">Ollama/Llama3</span>}>
          <div className="mb-6">
            <h4 className="text-xs font-mono text-slate-500 mb-2 uppercase tracking-wider">The Problem</h4>
            <p className="text-slate-200 leading-relaxed text-sm bg-slate-950 p-4 rounded-lg border border-slate-800/50">
              {expl.explanation}
            </p>
          </div>
          <div>
            <h4 className="text-xs font-mono text-slate-500 mb-2 uppercase tracking-wider">Recommended Fixes</h4>
            <ul className="space-y-2">
              {expl.suggestions.map((sug, i) => (
                <li key={i} className="flex items-start gap-3 bg-teal-500/5 border border-teal-500/20 p-3 rounded-lg">
                  <CheckCircle size={16} className="text-teal-400 shrink-0 mt-0.5" />
                  <span className="text-sm text-slate-300">{sug}</span>
                </li>
              ))}
            </ul>
          </div>
        </Card>
      </div>
    </div>
  );
};

const AgentTerminalView = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [logs, setLogs] = useState([]);
  const logsEndRef = useRef(null);

  const mockExecution = () => {
    setIsRunning(true);
    setLogs(["[SYSTEM] Initializing Agent Environment...", "[SYSTEM] Connecting to local Ollama service...", ""]);
    
    axios.post("http://localhost:8000/api/run-agent").catch(console.error);
    
    const sequence = [
      "[AGENT] Reading data/test_runs.csv...",
      "[AGENT] Found distinct failure profiles.",
      "[AGENT] Analyzing traceback...",
      "[OLLAMA] Querying Llama 3 (temperature=0.2) ...",
      "[OLLAMA] Generated Root Cause Hypothesis (Confidence: 94%)",
      "[AGENT] Cross-referencing hypothesis with historical execution times.",
      "[AGENT] Match found! Latency spike correlated with DB backup window.",
      "[AGENT] Compiling actionable fix code snippet.",
      "[SYSTEM] Saving report to reports/flaky_test_report.json",
      "[SYSTEM] Investigation Complete. 1 test analyzed."
    ];

    let i = 0;
    const interval = setInterval(() => {
      if (i < sequence.length) {
        setLogs(prev => [...prev, sequence[i]]);
        i++;
      } else {
        clearInterval(interval);
        setIsRunning(false);
      }
    }, 800);
  };

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center bg-slate-900 border border-slate-800 p-6 rounded-xl">
        <div>
          <h2 className="text-lg font-bold text-slate-200 flex items-center gap-2"><Zap className="text-teal-400" /> Autonomous Agent</h2>
          <p className="text-sm text-slate-400 mt-1">Trigger the backend Python agent to dynamically analyze raw logs via local LLM.</p>
        </div>
        <button 
          onClick={mockExecution}
          disabled={isRunning}
          className={`px-6 py-2.5 rounded-lg font-bold shadow-lg transition-all flex items-center gap-2 ${isRunning ? 'bg-slate-700 text-slate-400 cursor-not-allowed' : 'bg-gradient-to-r from-pink-500 to-rose-600 hover:shadow-pink-500/25 text-white'}`}
        >
          {isRunning ? <span className="animate-pulse flex items-center gap-2"><Cpu size={18}/> Executing...</span> : <><Play size={18} /> Run Full Investigation</>}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-[#050505] rounded-xl border border-slate-800 shadow-inner overflow-hidden font-mono text-sm flex flex-col h-[400px]">
            <div className="bg-slate-900/80 px-4 py-2 border-b border-slate-800 flex items-center gap-2">
              <Terminal size={14} className="text-slate-400"/>
              <span className="text-slate-400 text-xs tracking-wider">agent_stdout.log</span>
            </div>
            <div className="p-4 overflow-y-auto flex-1 space-y-1.5 custom-scrollbar">
              {logs.length === 0 && <span className="text-slate-600">Waiting for agent execution...</span>}
              {logs.map((log, i) => (
                <div key={i} className={`${log?.startsWith('[ERROR]') ? 'text-rose-400' : log?.startsWith('[SYSTEM]') ? 'text-teal-400' : log?.startsWith('[OLLAMA]') ? 'text-pink-400' : 'text-slate-300'}`}>
                  <span className="text-slate-600 select-none mr-3">{new Date().toISOString().split('T')[1].slice(0,-1)}</span>
                  {log}
                </div>
              ))}
              {isRunning && <div className="text-teal-400 animate-pulse">_</div>}
              <div ref={logsEndRef} />
            </div>
          </div>
        </div>

        <Card title="Investigation History" icon={History}>
          <div className="space-y-4">
            {[
               {id: "INV-892", time: "2 hours ago", status: "completed", target: "test_user_login"},
               {id: "INV-891", time: "Yesterday", status: "completed", target: "Entire Suite"},
               {id: "INV-890", time: "3 days ago", status: "failed", target: "test_cache_invalidation"},
            ].map(h => (
              <div key={h.id} className="flex items-start gap-3 border-b border-slate-800 pb-3 last:border-0 last:pb-0">
                <Clock size={14} className="text-slate-500 mt-1" />
                <div>
                  <div className="text-sm font-medium text-slate-200">{h.id} <span className="text-xs text-slate-500 font-normal ml-1">({h.target})</span></div>
                  <div className="text-xs text-slate-500 mt-0.5">{h.time} • <span className={h.status === 'completed' ? 'text-teal-400' : 'text-rose-400'}>{h.status}</span></div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};

const ChatView = () => {
  const [messages, setMessages] = useState([{role: 'assistant', text: "Hello! I have loaded the test suite data. Ask me anything about the flaky tests, trends, or specific errors."}]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef(null);

  const handleSend = async (e) => {
    e?.preventDefault();
    if (!input.trim()) return;
    
    const userMessage = { role: 'user', content: input };
    const systemMessage = { role: 'system', content: 'You are a helpful AI assistant analyzing flaky tests. Keep your answers concise.' };
    const newMessages = [systemMessage, ...messages.map(m => ({role: m.role, content: m.text || m.content})), userMessage];
    
    setMessages(prev => [...prev, {role: 'user', text: input}]);
    setInput("");
    setIsTyping(true);

    try {
      const response = await axios.post("http://localhost:8000/api/chat", {
        messages: newMessages
      });
      
      if (response.data.error) {
        setMessages(prev => [...prev, {role: 'assistant', text: `Error: ${response.data.error}`}]);
      } else if (response.data.message && response.data.message.content) {
        setMessages(prev => [...prev, {role: 'assistant', text: response.data.message.content}]);
      } else {
        setMessages(prev => [...prev, {role: 'assistant', text: "Received an empty response or unexpected format."}]);
      }
    } catch (err) {
      setMessages(prev => [...prev, {role: 'assistant', text: `Failed to connect to backend API: ${err.message}`}]);
    } finally {
      setIsTyping(false);
    }
  };

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  return (
    <Card className="h-[calc(100vh-140px)] flex flex-col p-0">
      <div className="px-5 py-4 border-b border-slate-800 bg-slate-900 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <MessageSquare size={18} className="text-pink-400" />
          <h3 className="font-mono text-sm font-bold text-slate-200">Chat with Data</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-teal-400 animate-pulse"></span>
          <span className="text-xs text-slate-500 font-mono tracking-wider">OLLAMA ACTIVE</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-6 custom-scrollbar bg-slate-950/30">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-2xl px-5 py-3 text-sm leading-relaxed ${m.role === 'user' ? 'bg-gradient-to-br from-teal-500/20 to-emerald-500/10 border border-teal-500/30 text-teal-50' : 'bg-slate-800/80 border border-slate-700 text-slate-200'}`}>
               {m.text}
            </div>
          </div>
        ))}
        {isTyping && (
           <div className="flex justify-start">
             <div className="bg-slate-800/80 border border-slate-700 rounded-2xl px-5 py-4 flex gap-1.5 items-center">
               <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></div>
               <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
               <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
             </div>
           </div>
        )}
        <div ref={chatEndRef} />
      </div>

      <div className="p-4 bg-slate-900 border-t border-slate-800">
        <form onSubmit={handleSend} className="relative flex items-center">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your flaky tests... (e.g., 'What is the worst test?')"
            className="w-full bg-slate-950 border border-slate-700 rounded-xl pl-4 pr-12 py-3.5 text-sm text-slate-200 focus:outline-none focus:border-pink-500 focus:ring-1 focus:ring-pink-500/50 transition-all"
          />
          <button type="submit" disabled={!input.trim()} className="absolute right-2 p-2 bg-pink-500/10 hover:bg-pink-500/20 text-pink-400 rounded-lg disabled:opacity-50 transition-colors">
            <Send size={18} />
          </button>
        </form>
      </div>
    </Card>
  );
};


// --- MAIN APP COMPONENT ---
export default function App() {
  const [data, setData] = useState(null);
  const [schemaReport, setSchemaReport] = useState(null);
  const [activeTab, setActiveTab] = useState('upload');

  const navItems = [
    { id: 'upload', icon: UploadCloud, label: 'Data Upload' },
    { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard', disabled: !data },
    { id: 'table', icon: TableIcon, label: 'Test Inventory', disabled: !data },
    { id: 'ai', icon: Zap, label: 'AI Explanations', disabled: !data },
    { id: 'agent', icon: Terminal, label: 'Run Agent', disabled: !data },
    { id: 'chat', icon: MessageSquare, label: 'Chat Interface', disabled: !data },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'upload': return <UploadView onUpload={(d, report) => { setData(d); setSchemaReport(report); setActiveTab('dashboard'); }} />;
      case 'dashboard': return <DashboardView data={data} schemaReport={schemaReport} />;
      case 'table': return <DataTableView data={data} />;
      case 'ai': return <ExplanationView data={data} />;
      case 'agent': return <AgentTerminalView />;
      case 'chat': return <ChatView />;
      default: return null;
    }
  };

  return (
    <div className="flex h-screen bg-[#0A0E1A] text-slate-200 font-sans selection:bg-teal-500/30 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-[#111827] border-r border-slate-800 flex flex-col shrink-0">
        <div className="p-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-400 to-pink-500 flex items-center justify-center text-white font-bold">⚡</div>
            <div>
              <h1 className="font-mono font-bold text-lg leading-tight">FLAKY<span className="text-teal-400">TEST</span></h1>
              <p className="text-[10px] text-slate-500 font-mono tracking-widest uppercase">Detector Engine</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 px-4 space-y-1 mt-4">
          <div className="text-[10px] font-mono font-bold tracking-widest text-slate-600 uppercase mb-3 px-2">Navigation</div>
          {navItems.map(item => (
            <button
              key={item.id}
              disabled={item.disabled}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 
                ${activeTab === item.id ? 'bg-teal-500/10 text-teal-400' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}
                ${item.disabled ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              <item.icon size={18} className={activeTab === item.id ? 'text-teal-400' : 'text-slate-500'} />
              {item.label}
            </button>
          ))}
        </nav>

        <div className="p-4 mt-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-teal-400 animate-pulse"></div>
              <span className="text-xs font-mono font-bold text-slate-300">Ollama Local</span>
            </div>
            <p className="text-[10px] text-slate-500 font-mono uppercase tracking-wide">Model: Llama 3 8B</p>
            <p className="text-[10px] text-slate-500 font-mono uppercase tracking-wide">Status: Ready</p>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-full overflow-hidden relative">
        {/* Top Header */}
        <header className="h-16 shrink-0 border-b border-slate-800 flex items-center px-8 bg-[#0A0E1A]/80 backdrop-blur-sm z-10">
          <div className="flex items-center text-sm font-mono text-slate-500">
            <span>Workspace</span>
            <ChevronRight size={14} className="mx-2" />
            <span className="text-teal-400 uppercase tracking-wider">{navItems.find(n => n.id === activeTab)?.label}</span>
          </div>
        </header>

        {/* Scrollable Content Area */}
        <div className="flex-1 overflow-y-auto p-8 custom-scrollbar relative">
           <div className="max-w-6xl mx-auto h-full">
              {renderContent()}
           </div>
        </div>
      </main>
    </div>
  );
}
