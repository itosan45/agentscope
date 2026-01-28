import React, { useState, useEffect } from 'react';
import { Activity, LayoutDashboard, Database, Bell, Settings, Search, Filter, ExternalLink, Clock, DollarSign, Cpu } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:10000/api/v1';
const PROJECT_ID = 'default-project';

interface Trace {
  id: string;
  name: string;
  status: string;
  duration_ms: number;
  total_tokens: number;
  total_cost_usd: number;
  created_at: string;
  span_count: number;
}

interface Metrics {
  total_traces: number;
  avg_duration_ms: number;
  total_cost_usd: number;
  error_rate: number;
}

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [traces, setTraces] = useState<Trace[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [tracesRes, metricsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/traces?project_id=${PROJECT_ID}`),
        axios.get(`${API_BASE_URL}/metrics?project_id=${PROJECT_ID}`)
      ]);
      setTraces(tracesRes.data);
      setMetrics(metricsRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // 5秒ごとに更新
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border bg-card flex flex-col">
        <div className="p-6 flex items-center gap-3">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center neon-glow-blue">
            <Activity className="w-5 h-5 text-primary-foreground" />
          </div>
          <h1 className="text-xl font-bold tracking-tight">AgentScope</h1>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-4">
          <NavItem
            icon={<LayoutDashboard size={20} />}
            label="Dashboard"
            active={activeTab === 'dashboard'}
            onClick={() => setActiveTab('dashboard')}
          />
          <NavItem
            icon={<Database size={20} />}
            label="Traces"
            active={activeTab === 'traces'}
            onClick={() => setActiveTab('traces')}
          />
          <NavItem
            icon={<Activity size={20} />}
            label="Metrics"
            active={activeTab === 'metrics'}
            onClick={() => setActiveTab('metrics')}
          />
          <NavItem
            icon={<Bell size={20} />}
            label="Alerts"
            active={activeTab === 'alerts'}
            onClick={() => setActiveTab('alerts')}
          />
        </nav>

        <div className="p-4 border-t border-border mt-auto">
          <NavItem icon={<Settings size={20} />} label="Settings" active={false} onClick={() => { }} />
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-16 border-b border-border flex items-center justify-between px-8 bg-background/50 backdrop-blur-sm sticky top-0 z-10">
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>Projects</span>
            <span>/</span>
            <span className="text-foreground font-medium">{PROJECT_ID}</span>
          </div>
          <div className="flex items-center gap-4">
            <div className={`px-3 py-1 bg-secondary rounded-full text-xs font-medium border ${loading ? 'text-muted-foreground border-border' : 'text-neon-blue border-neon-blue/20 animate-pulse'}`}>
              {loading ? 'Updating...' : 'Live Monitoring Active'}
            </div>
            <button onClick={fetchData} className="p-2 hover:bg-secondary rounded-lg transition-colors" aria-label="Refresh data">
              <Activity size={18} className="text-muted-foreground" />
            </button>
          </div>
        </header>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-8 space-y-8">
          {/* Stats Bar */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <StatCard icon={<Database className="text-neon-blue" />} label="Total Traces" value={metrics?.total_traces?.toString() || '0'} change="+12.5%" />
            <StatCard icon={<Clock className="text-neon-purple" />} label="Avg. Latency" value={`${((metrics?.avg_duration_ms || 0) / 1000).toFixed(1)}s`} change="-4.2%" />
            <StatCard icon={<DollarSign className="text-neon-green" />} label="Total Cost" value={`$${(metrics?.total_cost_usd || 0).toFixed(4)}`} change="+8.1%" />
            <StatCard icon={<Cpu className="text-destructive" />} label="Error Rate" value={`${(metrics?.error_rate || 0).toFixed(1)}%`} change="-1.5%" trend="down" />
          </div>

          {/* Trace Table Area */}
          <div className="glass-card flex flex-col min-h-[400px]">
            <div className="p-6 border-b border-border flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold tracking-tight">Recent Traces</h2>
                <p className="text-xs text-muted-foreground mt-1 uppercase tracking-widest">Latest executions from AI agents</p>
              </div>
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search traces..."
                    className="pl-10 pr-4 py-1.5 bg-background border border-border rounded-lg text-sm focus:ring-1 focus:ring-primary outline-none"
                  />
                </div>
                <button className="p-2 bg-secondary border border-border rounded-lg hover:bg-muted transition-colors" aria-label="Filter traces">
                  <Filter size={16} />
                </button>
              </div>
            </div>

            <div className="overflow-x-auto flex-1">
              <table className="w-full text-left">
                <thead className="text-xs uppercase text-muted-foreground bg-muted/50 border-b border-border">
                  <tr>
                    <th className="px-6 py-4 font-medium">Trace Name</th>
                    <th className="px-6 py-4 font-medium">Status</th>
                    <th className="px-6 py-4 font-medium">Steps</th>
                    <th className="px-6 py-4 font-medium">Duration</th>
                    <th className="px-6 py-4 font-medium">Cost</th>
                    <th className="px-6 py-4 font-medium">Time</th>
                    <th className="px-6 py-4 font-medium"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {traces.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="px-6 py-20 text-center text-muted-foreground">
                        <Activity className="w-12 h-12 mx-auto mb-4 opacity-20" />
                        <p>No traces found yet. Start sending data with AgentScope SDK.</p>
                      </td>
                    </tr>
                  ) : (
                    traces.map((trace) => (
                      <tr key={trace.id} className="hover:bg-muted/30 transition-colors group">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className={`w-2 h-2 rounded-full ${trace.status === 'success' ? 'bg-neon-green shadow-[0_0_8px_rgba(0,255,65,0.4)]' : 'bg-destructive shadow-[0_0_8px_rgba(239,68,68,0.4)]'}`}></div>
                            <span className="font-medium tracking-tight">{trace.name}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] uppercase font-bold tracking-widest ${trace.status === 'success' ? 'bg-neon-green/10 text-neon-green border border-neon-green/20' : 'bg-destructive/10 text-destructive border border-destructive/20'
                            }`}>
                            {trace.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-muted-foreground">
                          {trace.span_count} steps
                        </td>
                        <td className="px-6 py-4 text-sm font-mono text-muted-foreground">
                          {trace.duration_ms}ms
                        </td>
                        <td className="px-6 py-4 text-sm font-mono text-muted-foreground">
                          ${(trace.total_cost_usd || 0).toFixed(4)}
                        </td>
                        <td className="px-6 py-4 text-sm text-muted-foreground">
                          {new Date(trace.created_at).toLocaleTimeString()}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <button className="p-2 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-secondary rounded-lg" aria-label="View trace details">
                            <ExternalLink size={14} className="text-primary" />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            <div className="p-4 border-t border-border bg-muted/20 text-center">
              <button className="text-sm text-primary hover:underline font-medium">View detailed execution history</button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function NavItem({ icon, label, active, onClick }: { icon: React.ReactNode, label: string, active: boolean, onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${active
        ? 'bg-primary/10 text-primary border border-primary/20 shadow-[0_0_15px_rgba(59,130,246,0.1)]'
        : 'text-muted-foreground hover:bg-muted hover:text-foreground'
        }`}
    >
      {icon}
      <span>{label}</span>
    </button>
  );
}

function StatCard({ icon, label, value, change, trend = "up" }: { icon: React.ReactNode, label: string, value: string, change: string, trend?: "up" | "down" }) {
  return (
    <div className="glass-card p-6 flex flex-col gap-2 relative overflow-hidden group">
      <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
        {React.isValidElement(icon) ? React.cloneElement(icon as React.ReactElement<any>, { size: 48 }) : icon}
      </div>
      <span className="text-xs font-bold uppercase tracking-widest text-muted-foreground">{label}</span>
      <div className="flex items-end justify-between mt-1">
        <span className="text-3xl font-bold tracking-tight">{value}</span>
        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${trend === 'up' ? 'bg-neon-green/10 text-neon-green border-neon-green/20' : 'bg-destructive/10 text-destructive border-destructive/20'
          }`}>
          {change}
        </span>
      </div>
    </div>
  );
}

export default App;
