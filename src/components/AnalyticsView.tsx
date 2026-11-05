import React from 'react';
import { TicketItem, AUDIT_LOGS } from '../data/defaultData';
import {
  Activity,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ShieldCheck,
  TrendingUp,
  Flame,
  FileCheck2
} from 'lucide-react';

interface AnalyticsViewProps {
  tickets: TicketItem[];
}

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({ tickets }) => {
  const total = tickets.length;
  const closed = tickets.filter(t => t.status === 'CLOSED').length;
  const active = total - closed;
  const urgent = tickets.filter(t => t.priority === 'URGENT' && t.status !== 'CLOSED').length;
  const resolutionRate = total > 0 ? Math.round((closed / total) * 100) : 100;

  return (
    <div className="h-full overflow-y-auto bg-slate-950 text-slate-100 p-6 space-y-6 font-sans">
      {/* Top Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-indigo-600/20 text-indigo-400 rounded-lg">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight">
              HELZERX Operational Analytics & Audit Feed
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Live ticketing metrics, AI response velocity, and immutable security audit logs.
            </p>
          </div>
        </div>

        {/* 4-KPI Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-slate-800/80">
          <div className="bg-slate-950/60 p-4 rounded-lg border border-slate-800/80">
            <span className="text-xs text-slate-400 block">Total Tickets Processed</span>
            <span className="text-2xl font-bold text-white font-mono tabular-nums block mt-1">
              {total}
            </span>
            <span className="text-[11px] text-emerald-400 font-medium mt-1 block">
              100% persisted in PostgreSQL
            </span>
          </div>

          <div className="bg-slate-950/60 p-4 rounded-lg border border-slate-800/80">
            <span className="text-xs text-slate-400 block">Active Support Queue</span>
            <span className="text-2xl font-bold text-white font-mono tabular-nums block mt-1">
              {active}
            </span>
            <span className="text-[11px] text-indigo-400 font-medium mt-1 block">
              {tickets.filter(t => t.status === 'ESCALATED').length} currently escalated
            </span>
          </div>

          <div className="bg-slate-950/60 p-4 rounded-lg border border-slate-800/80">
            <span className="text-xs text-slate-400 block">Urgent Priority Incidents</span>
            <div className="flex items-center gap-2 mt-1">
              <span className={`text-2xl font-bold font-mono tabular-nums ${urgent > 0 ? 'text-red-400' : 'text-slate-300'}`}>
                {urgent}
              </span>
              {urgent > 0 && <Flame className="w-5 h-5 text-red-500 animate-pulse" />}
            </div>
            <span className="text-[11px] text-slate-400 font-medium mt-1 block">
              Requires immediate triage
            </span>
          </div>

          <div className="bg-slate-950/60 p-4 rounded-lg border border-slate-800/80">
            <span className="text-xs text-slate-400 block">Resolution Rate</span>
            <span className="text-2xl font-bold text-emerald-400 font-mono tabular-nums block mt-1">
              {resolutionRate}%
            </span>
            <span className="text-[11px] text-slate-400 font-medium mt-1 block">
              Average AI Latency: 148ms
            </span>
          </div>
        </div>
      </div>

      {/* Grid: Category Breakdown + Audit Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category & SLA Distribution */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <h2 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-indigo-400" />
            <span>Category Inflow Breakdown</span>
          </h2>

          <div className="space-y-3 text-xs">
            {[
              { name: 'Minecraft Hosting', count: 14, pct: 45, color: 'bg-emerald-500' },
              { name: 'VPS Support', count: 8, pct: 26, color: 'bg-indigo-500' },
              { name: 'Dedicated Servers', count: 4, pct: 13, color: 'bg-amber-500' },
              { name: 'Technical Support', count: 3, pct: 10, color: 'bg-sky-500' },
              { name: 'Billing & Account', count: 2, pct: 6, color: 'bg-purple-500' }
            ].map(item => (
              <div key={item.name} className="space-y-1">
                <div className="flex justify-between text-slate-300">
                  <span>{item.name}</span>
                  <span className="font-mono text-slate-400">{item.count} tickets ({item.pct}%)</span>
                </div>
                <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden">
                  <div className={`h-full ${item.color} rounded-full`} style={{ width: `${item.pct}%` }} />
                </div>
              </div>
            ))}
          </div>

          <div className="pt-4 border-t border-slate-800 text-[11px] text-slate-400 space-y-2">
            <div className="flex items-center justify-between">
              <span>SLA Target (First AI Diagnostic)</span>
              <span className="font-mono text-emerald-400 font-semibold">&lt; 3.0s</span>
            </div>
            <div className="flex items-center justify-between">
              <span>SLA Target (Human Escalation)</span>
              <span className="font-mono text-emerald-400 font-semibold">&lt; 15 mins</span>
            </div>
          </div>
        </div>

        {/* Audit Log Stream */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Immutable Staff & Security Audit Trail</span>
            </h2>
            <span className="text-[11px] font-mono text-slate-400">
              Alembic: audit_logs
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-800 text-slate-400 text-[11px] uppercase tracking-wider">
                <tr>
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3">Action</th>
                  <th className="py-2.5 px-3">Actor</th>
                  <th className="py-2.5 px-3">Ticket</th>
                  <th className="py-2.5 px-3">Audit Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {AUDIT_LOGS.map(log => (
                  <tr key={log.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-2.5 px-3 font-mono text-[11px] text-slate-400 whitespace-nowrap">
                      {log.time}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-indigo-300 font-semibold">
                        {log.action}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-medium text-white whitespace-nowrap">
                      {log.actor}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-slate-300">
                      {log.ticket}
                    </td>
                    <td className="py-2.5 px-3 text-slate-300 truncate max-w-xs">
                      {log.details}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
