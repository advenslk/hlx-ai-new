import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { DiscordSimulator } from './components/DiscordSimulator';
import { AIDiagnostics } from './components/AIDiagnostics';
import { KnowledgeBase } from './components/KnowledgeBase';
import { AnalyticsView } from './components/AnalyticsView';
import { CodebaseViewer } from './components/CodebaseViewer';
import { INITIAL_TICKETS, TicketItem, TICKET_CATEGORIES, MessageItem } from './data/defaultData';

export default function App() {
  const [activeTab, setActiveTab] = useState<'simulator' | 'ai-lab' | 'knowledge' | 'analytics' | 'codebase'>('simulator');
  const [tickets, setTickets] = useState<TicketItem[]>(INITIAL_TICKETS);
  const [activeTicketId, setActiveTicketId] = useState<string | null>(INITIAL_TICKETS[0].id);
  const [showGlobalModal, setShowGlobalModal] = useState<boolean>(false);
  const [modalCat, setModalCat] = useState<string>('minecraft');
  const [modalSub, setModalSub] = useState<string>('');
  const [modalDesc, setModalDesc] = useState<string>('');
  const [modalNode, setModalNode] = useState<string>('');

  // Ticket creation handler
  const handleCreateTicket = (category: string, subject: string, description: string, serverId: string) => {
    const catDef = TICKET_CATEGORIES.find(c => c.id === category) || TICKET_CATEGORIES[0];
    const digits = Math.floor(1000 + Math.random() * 9000);
    const code = `HZX-${digits}`;

    // Auto priority check
    const textLower = `${subject} ${description}`.toLowerCase();
    let priority: 'LOW' | 'NORMAL' | 'HIGH' | 'URGENT' = catDef.defaultPriority;
    if (['down', 'offline', 'crashed', 'ddos', 'outage', 'attack'].some(w => textLower.includes(w))) {
      priority = 'URGENT';
    }

    const newTicket: TicketItem = {
      id: `t-${Date.now()}`,
      code,
      category,
      categoryName: catDef.name,
      priority,
      status: 'OPEN',
      creator: 'You (Alex)',
      subject,
      description,
      serverIdentifier: serverId || undefined,
      aiEnabled: true,
      createdAt: 'Just now',
      messages: [
        {
          id: `m-init-${Date.now()}`,
          authorName: 'You (Alex)',
          authorRole: 'customer',
          content: `**Subject:** ${subject}\n\n${description}`,
          timestamp: 'Just now',
          detectedLang: 'en'
        },
        {
          id: `m-ai-${Date.now()}`,
          authorName: 'HELZERX AI Support',
          authorRole: 'ai',
          content: `Hello! I have registered your ticket (**${code}**) and analyzed your report against the **HELZERX Verified Knowledge Base**.\n\nOur automated diagnostic service has scheduled checks on node \`${serverId || 'colombo-01'}\`. If this issue involves container startup errors or memory allocations, ensure your \`-Xmx\` is tuned properly with Aikar's flags, or reply with your \`latest.log\` file so I can diagnose immediately.\n\nType anytime, or summon human staff by clicking **Request Human Staff**!`,
          timestamp: 'Just now',
          detectedLang: 'en',
          latencyMs: 135
        }
      ],
      internalNotes: []
    };

    setTickets([newTicket, ...tickets]);
    setActiveTicketId(newTicket.id);
    setActiveTab('simulator');
  };

  // Close ticket handler
  const handleCloseTicket = (ticketId: string, reason?: string) => {
    setTickets(tickets.map(t => {
      if (t.id === ticketId) {
        return {
          ...t,
          status: 'CLOSED',
          closedAt: 'Just now',
          messages: [
            ...t.messages,
            {
              id: `m-close-${Date.now()}`,
              authorName: 'System',
              authorRole: 'system',
              content: `🔒 **Ticket Closed**: Marked as resolved by staff (${reason || 'Customer confirmation'}). Standalone HTML transcript archived.`,
              timestamp: 'Just now'
            }
          ]
        };
      }
      return t;
    }));
  };

  // Claim ticket handler
  const handleClaimTicket = (ticketId: string, staffName: string) => {
    setTickets(tickets.map(t => {
      if (t.id === ticketId) {
        return {
          ...t,
          status: 'CLAIMED',
          claimedBy: staffName,
          messages: [
            ...t.messages,
            {
              id: `m-claim-${Date.now()}`,
              authorName: 'System',
              authorRole: 'system',
              content: `✋ **Ticket Claimed**: ${staffName} is now the primary assigned engineer for this ticket.`,
              timestamp: 'Just now'
            }
          ]
        };
      }
      return t;
    }));
  };

  // Escalate ticket handler
  const handleEscalateTicket = (ticketId: string, reason: string) => {
    setTickets(tickets.map(t => {
      if (t.id === ticketId) {
        return {
          ...t,
          status: 'ESCALATED',
          aiEnabled: false,
          priority: t.priority === 'LOW' ? 'HIGH' : t.priority,
          messages: [
            ...t.messages,
            {
              id: `m-esc-${Date.now()}`,
              authorName: 'System',
              authorRole: 'system',
              content: `🔔 **Escalated to Human Support**: Ticket transferred to on-duty HELZERX technical staff. (${reason})`,
              timestamp: 'Just now'
            }
          ]
        };
      }
      return t;
    }));
  };

  // Add message handler
  const handleAddMessage = (ticketId: string, message: MessageItem) => {
    setTickets(tickets.map(t => {
      if (t.id === ticketId) {
        return {
          ...t,
          messages: [...t.messages, message]
        };
      }
      return t;
    }));
  };

  // Add internal note handler
  const handleAddInternalNote = (ticketId: string, note: string, author: string) => {
    setTickets(tickets.map(t => {
      if (t.id === ticketId) {
        return {
          ...t,
          internalNotes: [
            ...t.internalNotes,
            {
              id: `note-${Date.now()}`,
              author,
              content: note,
              timestamp: 'Just now'
            }
          ]
        };
      }
      return t;
    }));
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Top Bar adhering strictly to Top Bar Contract */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenNewTicketModal={() => setShowGlobalModal(true)}
      />

      {/* Main View Area */}
      <main className="flex-1 overflow-hidden relative">
        {activeTab === 'simulator' && (
          <DiscordSimulator
            tickets={tickets}
            activeTicketId={activeTicketId}
            setActiveTicketId={setActiveTicketId}
            onCreateTicket={handleCreateTicket}
            onCloseTicket={handleCloseTicket}
            onClaimTicket={handleClaimTicket}
            onEscalateTicket={handleEscalateTicket}
            onAddMessage={handleAddMessage}
            onAddInternalNote={handleAddInternalNote}
          />
        )}

        {activeTab === 'ai-lab' && <AIDiagnostics />}

        {activeTab === 'knowledge' && <KnowledgeBase />}

        {activeTab === 'analytics' && <AnalyticsView tickets={tickets} />}

        {activeTab === 'codebase' && <CodebaseViewer />}
      </main>

      {/* Global Quick Open Ticket Modal */}
      {showGlobalModal && (
        <div className="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white">Create HELZERX Support Ticket</h3>
              <button onClick={() => setShowGlobalModal(false)} className="text-slate-400 hover:text-white cursor-pointer">
                ✕
              </button>
            </div>

            <div className="space-y-3 text-sm">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Department</label>
                <select
                  value={modalCat}
                  onChange={e => setModalCat(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-md p-2 text-white"
                >
                  {TICKET_CATEGORIES.map(c => (
                    <option key={c.id} value={c.id}>{c.emoji} {c.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Brief Subject Summary *</label>
                <input
                  type="text"
                  value={modalSub}
                  onChange={e => setModalSub(e.target.value)}
                  placeholder="e.g. VPS networking routing packet loss"
                  className="w-full bg-slate-950 border border-slate-800 rounded-md p-2 text-white placeholder-slate-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Detailed Description *</label>
                <textarea
                  rows={4}
                  value={modalDesc}
                  onChange={e => setModalDesc(e.target.value)}
                  placeholder="Describe the issue, paste error logs (English, Sinhala, Singlish)..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-md p-2 text-white placeholder-slate-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Server / Node Identifier</label>
                <input
                  type="text"
                  value={modalNode}
                  onChange={e => setModalNode(e.target.value)}
                  placeholder="e.g. node-04 / vps-8812"
                  className="w-full bg-slate-950 border border-slate-800 rounded-md p-2 text-white placeholder-slate-500"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-slate-800">
              <button
                onClick={() => setShowGlobalModal(false)}
                className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (!modalSub.trim() || !modalDesc.trim()) return;
                  handleCreateTicket(modalCat, modalSub, modalDesc, modalNode);
                  setShowGlobalModal(false);
                  setModalSub('');
                  setModalDesc('');
                  setModalNode('');
                }}
                disabled={!modalSub.trim() || !modalDesc.trim()}
                className="px-5 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-md transition-colors cursor-pointer disabled:opacity-50"
              >
                Submit Ticket
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
