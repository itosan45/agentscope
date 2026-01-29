import React from 'react';
import { Activity, Shield, Zap, BarChart3, Github, Twitter } from 'lucide-react';
import { motion } from 'framer-motion';

function App() {
  return (
    <div className="min-h-screen relative overflow-hidden bg-grid-slate">
      <div className="hero-gradient pointer-events-none"></div>

      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 border-b border-white/5 bg-background/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 group cursor-pointer">
            <Activity className="w-6 h-6 text-primary group-hover:scale-110 transition-transform" />
            <span className="text-xl font-bold tracking-tight">AgentScope</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
            <a href="#docs" className="hover:text-white transition-colors">Docs</a>
          </div>
          <div>
            <a
              href="https://agentscope-dashboard-v3.onrender.com"
              className="px-4 py-2 bg-primary text-background font-bold rounded-full text-sm hover:scale-105 transition-transform active:scale-95 inline-block"
            >
              Launch App
            </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs font-bold text-primary mb-8"
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
            </span>
            PUBLIC BETA NOW OPEN
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8 bg-gradient-to-b from-white to-slate-400 bg-clip-text text-transparent"
          >
            AI Agents, <br />
            <span className="text-primary">Finally Visible.</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="max-w-2xl mx-auto text-lg md:text-xl text-slate-400 mb-12"
          >
            AgentScope is the developer-first observability platform for AI Agents.
            Trace every call, monitor costs in real-time, and catch errors before your users do.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <a
              href="https://buy.stripe.com/test_7sYaEXa6x9xH0Y71rs7EQ00"
              className="w-full sm:w-auto px-8 py-4 bg-primary text-background font-bold rounded-full text-lg shadow-[0_0_30px_rgba(56,189,248,0.3)] hover:shadow-[0_0_50px_rgba(56,189,248,0.5)] transition-all text-center"
            >
              Start Monitoring for Free
            </a>
            <a
              href="#features"
              className="w-full sm:w-auto px-8 py-4 bg-slate-900 border border-slate-800 font-bold rounded-full text-lg hover:bg-slate-800 transition-colors text-center"
            >
              Read Documentation
            </a>
          </motion.div>
        </div>
      </section>

      {/* Code Preview */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto glass-panel p-2 shadow-2xl">
          <div className="bg-background rounded-[22px] overflow-hidden border border-white/5">
            <div className="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-white/5">
              <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500/50"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500/50"></div>
                <div className="w-3 h-3 rounded-full bg-green-500/50"></div>
              </div>
              <span className="text-xs font-mono text-slate-500 uppercase tracking-widest">example_agent.py</span>
              <div className="w-12"></div>
            </div>
            <pre className="p-8 text-sm md:text-base font-mono overflow-x-auto leading-relaxed">
              <code className="text-slate-300">
                <span className="text-primary">import</span> agentscope <br />
                <br />
                agentscope.<span className="text-accent underline decoration-accent/30 underline-offset-4">init</span>(api_key=<span className="text-orange-400">"sk_..."</span>, project_id=<span className="text-orange-400">"my-bot"</span>)<br />
                <br />
                <span className="text-slate-500"># Monitor everything with one decorator</span><br />
                <span className="text-primary">@agentscope.trace()</span><br />
                <span className="text-primary">def</span> <span className="text-neon-cyan">weather_agent</span>(city):<br />
                &nbsp;&nbsp;response = openai.chat.completions.create(...)<br />
                &nbsp;&nbsp;<span className="text-primary">return</span> response<br />
              </code>
            </pre>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-20 px-6 bg-slate-950/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-3xl md:text-5xl font-bold mb-6">Built for the next generation <br />of AI developers.</h2>
            <p className="text-slate-400">Stop guessing what your agents are doing. Start seeing.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Zap className="text-yellow-400" />}
              title="1-Minute Setup"
              desc="Integrate into any existing Python agent with just two lines of code. Zero architectural changes required."
            />
            <FeatureCard
              icon={<Shield className="text-green-400" />}
              title="Audit Everything"
              desc="Every LLM call, tool use, and function execution is recorded with full input/output visibility."
            />
            <FeatureCard
              icon={<BarChart3 className="text-primary" />}
              title="Cost Optimization"
              desc="Real-time cost tracking per project and per model. Never be surprised by an OpenAI bill again."
            />
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-32 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-extrabold mb-16 tracking-tight">Simple Pricing. <span className="text-primary">Limitless Visibility.</span></h2>
          <div className="flex justify-center">
            <div className="w-full max-w-sm glass-panel p-10 bg-slate-900/50 border-primary/20 shadow-[0_0_50px_rgba(56,189,248,0.1)]">
              <h3 className="text-2xl font-bold mb-2">Pro Plan</h3>
              <div className="flex items-baseline justify-center gap-1 mb-6">
                <span className="text-5xl font-extrabold text-white">¥2,900</span>
                <span className="text-slate-500 font-medium">/month</span>
              </div>
              <ul className="text-left space-y-4 mb-10 text-slate-300">
                <li className="flex items-center gap-3">
                  <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center">
                    <div className="w-2 h-2 rounded-full bg-primary"></div>
                  </div>
                  Unlimited Traces
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center">
                    <div className="w-2 h-2 rounded-full bg-primary"></div>
                  </div>
                  Real-time Slack Alerts
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center">
                    <div className="w-2 h-2 rounded-full bg-primary"></div>
                  </div>
                  Full Input/Output Visibility
                </li>
              </ul>
              <a
                href="https://buy.stripe.com/test_7sYaEXa6x9xH0Y71rs7EQ00"
                className="block w-full py-4 bg-primary text-background font-extrabold rounded-full text-lg hover:scale-[1.02] transition-transform active:scale-95"
              >
                Get Started Now
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-20 border-t border-white/5 bg-background">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="flex items-center gap-2">
            <Activity className="w-6 h-6 text-primary" />
            <span className="text-xl font-bold tracking-tight">AgentScope</span>
          </div>
          <p className="text-slate-500 text-sm">© 2026 AgentScope Observability. All rights reserved.</p>
          <div className="flex items-center gap-4">
            <a href="#" className="p-2 text-slate-400 hover:text-white transition-colors" aria-label="AgentScope on Twitter"><Twitter size={20} /></a>
            <a href="#" className="p-2 text-slate-400 hover:text-white transition-colors" aria-label="AgentScope on GitHub"><Github size={20} /></a>
          </div>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, desc }: { icon: React.ReactNode, title: string, desc: string }) {
  return (
    <div className="glass-panel p-8 hover:bg-slate-900/50 transition-colors group">
      <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
        {icon}
      </div>
      <h3 className="text-xl font-bold mb-4">{title}</h3>
      <p className="text-slate-400 leading-relaxed text-sm">{desc}</p>
    </div>
  );
}

export default App;
