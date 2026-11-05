import React, { useState, useRef, useEffect } from 'react';
import {
  TicketItem,
  TICKET_CATEGORIES,
  MessageItem
} from '../data/defaultData';
import {
  Hash,
  Lock,
  Send,
  UserCheck,
  AlertCircle,
  FileText,
  XCircle,
  Shield,
  Eye,
  EyeOff,
  PlusCircle,
  CheckCircle2,
  Cpu,
  User
} from 'lucide-react';

interface DiscordSimulatorProps {
  tickets: TicketItem[];
  activeTicketId: string | null;
  setActiveTicketId: (id: string | null) => void;
  onCreateTicket: (category: string, subject: string, description: string, serverId: string) => void;
  onCloseTicket: (ticketId: string, reason?: string) => void;
  onClaimTicket: (ticketId: string, staffName: string) => void;
  onEscalateTicket: (ticketId: string, reason: string) => void;
  onAddMessage: (ticketId: string, message: MessageItem) => void;
  onAddInternalNote: (ticketId: string, note: string, author: string) => void;
}

export const DiscordSimulator: React.FC<DiscordSimulatorProps> = ({
  tickets,
  activeTicketId,
  setActiveTicketId,
  onCreateTicket,
  onCloseTicket,
  onClaimTicket,
  onEscalateTicket,
  onAddMessage,
  onAddInternalNote
}) => {
  const [selectedChannel, setSelectedChannel] = useState<string>('create-a-ticket');
  const [isStaffMode, setIsStaffMode] = useState<boolean>(true);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [isAiTyping, setIsAiTyping] = useState<boolean>(false);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [modalCategory, setModalCategory] = useState<string>('general');
  const [modalSubject, setModalSubject] = useState<string>('');
  const [modalDesc, setModalDesc] = useState<string>('');
  const [modalServerId, setModalServerId] = useState<string>('');
  const [showNoteModal, setShowNoteModal] = useState<boolean>(false);
  const [internalNoteText, setInternalNoteText] = useState<string>('');
  const [showCloseConfirm, setShowCloseConfirm] = useState<boolean>(false);
  const [closeReason, setCloseReason] = useState<string>('');
  const [securityNotice, setSecurityNotice] = useState<string | null>(null);

  // Dynamic ticket panel customization state (matches bot's !panel-setup and screenshot)
  const defaultScreenshotConfig = {
    is_active: true,
    title: '🎧 HelzerX Support Center 🎧',
    topLogoUrl: '/assets/helzerx-logo-3d.png',
    description: 'Need assistance? Our support team is here to help.\n\nCreate a ticket by selecting the appropriate category below. Please provide clear details so our team can assist you efficiently.',
    categoriesTitle: 'Support Categories',
    categoriesList: '• 👥 **General Support**\n• 📚 **Cloud & Hosting**\n• 🖥️ **Technical Issues**\n• 💳 **Billing & Payments**\n• 🚀 **Partnerships & Business**',
    noteTitle: 'Please Note',
    noteText: 'Submit one ticket per issue and keep all related communication within your ticket.',
    bannerUrl: '/assets/helzerx-banner.png',
    footerLine1: 'HelzerX Technologies',
    footerLine2: '© 2026 HelzerX Technologies (Pvt) Ltd. All rights reserved.',
    selectPlaceholder: 'Select a ticket category'
  };

  const [panelConfig, setPanelConfig] = useState(defaultScreenshotConfig);
  const [showBuilderDashboard, setShowBuilderDashboard] = useState<boolean>(false);
  const [activeBuilderModal, setActiveBuilderModal] = useState<'header' | 'intro' | 'categories' | 'note' | 'images' | 'footer' | null>(null);
  const [tempConfig, setTempConfig] = useState(defaultScreenshotConfig);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const activeTicket = tickets.find(t => t.id === activeTicketId);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeTicket?.messages, isAiTyping]);

  // Language & security helpers
  const detectLanguage = (text: string): 'en' | 'si' | 'singlish' => {
    const sinhalaRegex = /[\u0D80-\u0DFF]/;
    if (sinhalaRegex.test(text)) return 'si';
    const singlishWords = ['mage', 'mata', 'api', 'oyala', 'server eka', 'weda', 'wenne', 'nehe', 'help ekak', 'puluwanda', 'wings', 'danna', 'hadala'];
    const lower = text.toLowerCase();
    const count = singlishWords.filter(w => lower.includes(w)).length;
    if (count >= 1) return 'singlish';
    return 'en';
  };

  const checkPromptInjection = (text: string): boolean => {
    const injectionPatterns = [
      /ignore (all )?(previous|prior) instructions/i,
      /you are now (dan|unrestricted|god mode)/i,
      /print (your|the) system prompt/i,
      /repeat everything above/i,
      /system directive override/i
    ];
    return injectionPatterns.some(p => p.test(text));
  };

  const sanitizeInput = (text: string): { sanitized: string; hadSecret: boolean } => {
    let hadSecret = false;
    let s = text;
    if (/[\w-]{24}\.[\w-]{6}\.[\w-]{27,}/i.test(s)) {
      s = s.replace(/[\w-]{24}\.[\w-]{6}\.[\w-]{27,}/gi, '[REDACTED_DISCORD_TOKEN]');
      hadSecret = true;
    }
    if (/nvapi-[A-Za-z0-9_-]{30,}|sk-[A-Za-z0-9]{32,}/.test(s)) {
      s = s.replace(/nvapi-[A-Za-z0-9_-]{30,}|sk-[A-Za-z0-9]{32,}/g, '[REDACTED_API_KEY]');
      hadSecret = true;
    }
    if (/-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----/.test(s)) {
      s = s.replace(/-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----/g, '[REDACTED_SSH_KEY]');
      hadSecret = true;
    }
    if (/(password|secret|rcon\.password)\s*[:=]\s*([^\s,;]+)/i.test(s)) {
      s = s.replace(/(password|secret|rcon\.password)\s*[:=]\s*([^\s,;]+)/gi, '$1: [REDACTED_SECRET]');
      hadSecret = true;
    }
    return { sanitized: s, hadSecret };
  };

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;

    const raw = inputMessage;
    setInputMessage('');

    // Check for container builder commands: *panel, !panel, *panel-setup, !panel-setup
    const trimmed = raw.trim().toLowerCase();
    if (trimmed === '!panel-setup' || trimmed === '/panel-setup' || trimmed === '*panel-setup' || trimmed === '*panel') {
      setSelectedChannel('create-a-ticket');
      setShowBuilderDashboard(true);
      setSecurityNotice('🛠️ 📚 Ticket Panel Dashboard Activated: Customize your support panel and categories.');
      setTimeout(() => setSecurityNotice(null), 5000);
      return;
    }
    if (trimmed === '!panel' || trimmed === '/panel') {
      setSelectedChannel('create-a-ticket');
      setShowBuilderDashboard(true);
      setSecurityNotice('✅ Ticket Panel loaded in #1. create-a-ticket.');
      setTimeout(() => setSecurityNotice(null), 5000);
      return;
    }

    if (!activeTicket) return;

    // 1. Check prompt injection
    if (checkPromptInjection(raw)) {
      setSecurityNotice('Security Alert: System instruction override pattern detected and intercepted.');
      setTimeout(() => setSecurityNotice(null), 7000);

      const securityMsg: MessageItem = {
        id: `sec-${Date.now()}`,
        authorName: isStaffMode ? 'Staff_Member' : activeTicket.creator,
        authorRole: isStaffMode ? 'staff' : 'customer',
        content: raw,
        timestamp: 'Just now'
      };
      onAddMessage(activeTicket.id, securityMsg);

      setTimeout(() => {
        const responseMsg: MessageItem = {
          id: `ai-${Date.now()}`,
          authorName: 'HELZERX AI Support',
          authorRole: 'ai',
          content: '🛡️ **Security Intercept**: Your query was flagged by the HELZERX Security Filter for attempting system prompt extraction or instruction override. Please describe your technical server issue directly.',
          timestamp: 'Just now',
          detectedLang: 'en'
        };
        onAddMessage(activeTicket.id, responseMsg);
      }, 500);
      return;
    }

    // 2. Sensitive data sanitization
    const { sanitized, hadSecret } = sanitizeInput(raw);
    if (hadSecret) {
      setSecurityNotice('Sensitive Data Redacted: A credential or private token was masked in the message.');
      setTimeout(() => setSecurityNotice(null), 6000);
    }

    const detected = detectLanguage(sanitized);

    const userMsg: MessageItem = {
      id: `m-${Date.now()}`,
      authorName: isStaffMode ? 'SupportEngineer' : activeTicket.creator,
      authorRole: isStaffMode ? 'staff' : 'customer',
      content: sanitized,
      timestamp: 'Just now',
      detectedLang: detected
    };

    onAddMessage(activeTicket.id, userMsg);

    // If customer and AI enabled, generate response
    if (!isStaffMode && activeTicket.aiEnabled && activeTicket.status !== 'CLOSED') {
      setIsAiTyping(true);

      setTimeout(() => {
        setIsAiTyping(false);
        let aiReply = '';

        if (detected === 'singlish') {
          aiReply = `Ape diagnostic system eken oyaage issue eka analyze kala.\n\nPoddak me steps tika check karala balanna puluwanda:\n1. Server eke **latest.log** file eka open karala anthimata thiyena Error / Warning eka balanna.\n2. Container restart ekak dila Pterodactyl console eke port allocations hariyatama bind wenawada kiyala check karanna.\n\nOyaata meka thawa therenne nathnam mata ape **Human Support Staff** ekata direct escalate karanna puluwan.`;
        } else if (detected === 'si') {
          aiReply = `ඔබගේ ගැටලුව සම්බන්ධයෙන් අපගේ තාක්ෂණික පරීක්ෂාව සිදු කරන ලදී.\n\nකරුණාකර පහත පියවර අනුගමනය කරන්න:\n1. Pterodactyl Console එකේ දෝෂ පණිවිඩය (Error Log) පරීක්ෂා කරන්න.\n2. Java අනුවාදය (Java 17/21) නිවැරදිව තෝරාගෙන ඇති බව තහවුරු කරගන්න.\n\nඔබට වැඩිදුර උපකාර අවශ්‍ය නම් කාර්ය මණ්ඩල සහය (Human Staff) වෙත යොමු කළ හැක.`;
        } else {
          aiReply = `I've analyzed your report against the **HELZERX Knowledge Base**.\n\nHere are the recommended diagnostic steps:\n\n1. **Verify Network & Sockets**: If using Pterodactyl Wings, verify service status with \`systemctl status wings\` and ensure port **8080** is open.\n2. **Check Memory Headroom**: If container exit code is **137**, ensure \`-Xmx\` is lowered by 1GB to prevent off-heap Linux OOM termination.\n3. **DNS Proxying**: If linking custom domains via Cloudflare, ensure your Minecraft DNS record is **DNS Only (Grey Cloud)**.\n\nWould you like me to summon an on-duty human engineer to assist?`;
        }

        const aiMsg: MessageItem = {
          id: `ai-${Date.now()}`,
          authorName: 'HELZERX AI Support',
          authorRole: 'ai',
          content: aiReply,
          timestamp: 'Just now',
          detectedLang: detected,
          latencyMs: Math.floor(Math.random() * 120) + 110
        };
        onAddMessage(activeTicket.id, aiMsg);
      }, 1400);
    }
  };

  const handleDownloadTranscript = (ticket: TicketItem) => {
    const htmlContent = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>HELZERX Transcript - ${ticket.code}</title>
  <style>
    body { background: #0b0f19; color: #e2e8f0; font-family: sans-serif; padding: 24px; }
    .card { max-width: 800px; margin: auto; background: #111827; border: 1px solid #1f2937; border-radius: 8px; padding: 24px; }
    .header { border-bottom: 1px solid #374151; padding-bottom: 16px; margin-bottom: 16px; }
    .msg { margin: 12px 0; padding: 12px; background: #1f2937; border-radius: 6px; }
    .msg.ai { border-left: 4px solid #5865f2; }
    .msg.staff { border-left: 4px solid #10b981; }
    .author { font-weight: bold; color: #f9fafb; }
    .time { font-size: 11px; color: #9ca3af; margin-left: 8px; }
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <h2>HELZERX Support Transcript: ${ticket.code} (${ticket.categoryName})</h2>
      <p>Customer: ${ticket.creator} | Priority: ${ticket.priority} | Status: ${ticket.status}</p>
    </div>
    ${ticket.messages.map(m => `
      <div class="msg ${m.authorRole}">
        <span class="author">${m.authorName}</span><span class="time">${m.timestamp}</span>
        <div style="margin-top:6px; white-space:pre-wrap;">${m.content}</div>
      </div>
    `).join('')}
  </div>
</body>
</html>`;

    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcript_${ticket.code}.html`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex h-full w-full bg-[#1e1f22] text-[#dbdee1] overflow-hidden select-none font-sans">
      {/* 1. Discord Server List Bar */}
      <div className="w-[72px] bg-[#1e1f22] flex flex-col items-center py-3 gap-2.5 shrink-0 border-r border-[#232428]">
        <div className="w-12 h-12 rounded-2xl bg-indigo-600 flex items-center justify-center text-white font-bold text-lg shadow-md hover:rounded-xl transition-all cursor-pointer">
          HX
        </div>
        <div className="w-8 h-[2px] bg-[#35363c] rounded" />
        <div
          onClick={() => setSelectedChannel('open-a-ticket')}
          className="w-12 h-12 rounded-3xl hover:rounded-xl bg-[#313338] hover:bg-indigo-500 hover:text-white flex items-center justify-center transition-all cursor-pointer text-slate-300 relative group"
          title="Support Center"
        >
          <Hash className="w-6 h-6" />
        </div>
      </div>

      {/* 2. Channel Sidebar */}
      <div className="w-60 bg-[#2b2d31] flex flex-col shrink-0 border-r border-[#232428]">
        {/* Server Header */}
        <div className="h-12 px-4 border-b border-[#1f2023] flex items-center justify-between font-bold text-white text-sm shadow-xs">
          <span className="truncate">HELZERX Enterprise</span>
          <Shield className="w-4 h-4 text-emerald-400" />
        </div>

        {/* Channel Categories & List */}
        <div className="flex-1 overflow-y-auto px-2 py-3 space-y-4 text-xs font-semibold text-[#949ba4]">
          {/* General Support Category */}
          <div>
            <div className="px-2 py-1 uppercase tracking-wider text-[11px] font-bold text-[#80848e]">
              Support Desk
            </div>
            <div className="space-y-0.5 mt-1">
              <button
                onClick={() => {
                  setSelectedChannel('create-a-ticket');
                  setActiveTicketId(null);
                }}
                className={`w-full flex items-center gap-1.5 px-2 py-1.5 rounded text-left transition-colors cursor-pointer ${
                  selectedChannel === 'create-a-ticket'
                    ? 'bg-[#404249] text-white font-medium'
                    : 'hover:bg-[#35373c] hover:text-[#dbdee1]'
                }`}
              >
                <Hash className="w-4 h-4 text-[#80848e]" />
                <span className="truncate">1. create-a-ticket.</span>
              </button>
            </div>
          </div>

          {/* Active Tickets Category */}
          <div>
            <div className="px-2 py-1 uppercase tracking-wider text-[11px] font-bold text-[#80848e] flex items-center justify-between">
              <span>Active Tickets ({tickets.filter(t => t.status !== 'CLOSED').length})</span>
              <button
                onClick={() => setShowCreateModal(true)}
                className="hover:text-white transition-colors p-0.5 cursor-pointer"
                title="Create Ticket"
              >
                <PlusCircle className="w-3.5 h-3.5" />
              </button>
            </div>
            <div className="space-y-0.5 mt-1">
              {tickets.map(ticket => {
                const isCurrent = activeTicketId === ticket.id;
                const priorityColor =
                  ticket.priority === 'URGENT'
                    ? 'text-red-400'
                    : ticket.priority === 'HIGH'
                    ? 'text-amber-400'
                    : 'text-slate-400';

                return (
                  <button
                    key={ticket.id}
                    onClick={() => {
                      setActiveTicketId(ticket.id);
                      setSelectedChannel(ticket.id);
                    }}
                    className={`w-full flex items-center justify-between px-2 py-1.5 rounded text-left transition-colors cursor-pointer ${
                      isCurrent
                        ? 'bg-[#404249] text-white font-medium'
                        : 'hover:bg-[#35373c] hover:text-[#dbdee1]'
                    }`}
                  >
                    <div className="flex items-center gap-1.5 truncate">
                      <Lock className="w-3.5 h-3.5 text-[#80848e] shrink-0" />
                      <span className="truncate">{ticket.code.toLowerCase()}</span>
                    </div>
                    <span className={`text-[10px] uppercase font-mono ${priorityColor}`}>
                      {ticket.priority.slice(0, 3)}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* User Status Bar */}
        <div className="h-[52px] bg-[#232428] px-2.5 flex items-center justify-between">
          <div className="flex items-center gap-2 truncate">
            <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center text-white text-xs font-bold">
              {isStaffMode ? 'ST' : 'US'}
            </div>
            <div className="truncate text-left leading-tight">
              <div className="text-white text-xs font-semibold truncate">
                {isStaffMode ? 'SupportStaff#1042' : 'CustomerAlex#8821'}
              </div>
              <div className="text-[11px] text-[#949ba4] truncate">
                {isStaffMode ? 'HELZERX Staff' : 'Customer Account'}
              </div>
            </div>
          </div>
          <button
            onClick={() => setIsStaffMode(!isStaffMode)}
            className="p-1.5 hover:bg-[#313338] rounded text-[#b5bac1] hover:text-white transition-colors cursor-pointer"
            title={isStaffMode ? 'Switch to Customer View' : 'Switch to Staff View'}
          >
            {isStaffMode ? <Eye className="w-4 h-4 text-emerald-400" /> : <EyeOff className="w-4 h-4 text-slate-400" />}
          </button>
        </div>
      </div>

      {/* 3. Main Chat Viewport */}
      <div className="flex-1 flex flex-col bg-[#313338] overflow-hidden">
        {/* Channel Top Header */}
        <div className="h-12 border-b border-[#232428] px-4 flex items-center justify-between shrink-0 shadow-xs">
          <div className="flex items-center gap-2 text-white font-semibold text-sm">
            {selectedChannel === 'create-a-ticket' ? (
              <>
                <Hash className="w-5 h-5 text-[#80848e]" />
                <span>1. create-a-ticket.</span>
                <span className="text-xs text-[#949ba4] font-normal border-l border-[#3f4147] pl-3 ml-1">
                  Official HelzerX Support Center
                </span>
              </>
            ) : activeTicket ? (
              <>
                <Lock className="w-4 h-4 text-[#80848e]" />
                <span>{activeTicket.code.toLowerCase()}</span>
                <span className="text-xs text-[#949ba4] font-normal border-l border-[#3f4147] pl-3 ml-1 truncate">
                  {activeTicket.subject}
                </span>
              </>
            ) : (
              <span>Select or open a ticket</span>
            )}
          </div>

          {/* Mode Switcher Banner */}
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-[#949ba4]">Active Role:</span>
            <button
              onClick={() => setIsStaffMode(!isStaffMode)}
              className={`px-2.5 py-1 text-xs rounded font-medium transition-colors cursor-pointer flex items-center gap-1.5 ${
                isStaffMode
                  ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/80'
                  : 'bg-slate-800 text-slate-300 border border-slate-700'
              }`}
            >
              {isStaffMode ? <UserCheck className="w-3.5 h-3.5" /> : <User className="w-3.5 h-3.5" />}
              <span>{isStaffMode ? 'Staff Mode (Unlocked)' : 'Customer Mode'}</span>
            </button>
          </div>
        </div>

        {/* Security Notification Banner (if triggered) */}
        {securityNotice && (
          <div className="bg-amber-950/80 border-b border-amber-800 text-amber-200 px-4 py-2 text-xs flex items-center gap-2 animate-fade-in">
            <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
            <span>{securityNotice}</span>
          </div>
        )}

        {/* Messages / Viewport Body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {selectedChannel === 'create-a-ticket' && (
            <div className="max-w-2xl mx-auto py-2 space-y-4">
              {/* Quick Admin Customization Action */}
              <div className="flex items-center justify-between bg-[#1e1f22] p-2.5 rounded-lg border border-[#2b2d31]">
                <div className="flex items-center gap-2 text-xs text-[#949ba4]">
                  <span className="w-2 h-2 rounded-full bg-emerald-400" />
                  <span>Interactive Container Builder: <strong>!panel-setup</strong></span>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setShowBuilderDashboard(!showBuilderDashboard)}
                    className="px-3 py-1 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white rounded transition-colors cursor-pointer flex items-center gap-1.5"
                  >
                    <span>🛠️ {showBuilderDashboard ? 'Hide Builder' : 'Open Container Builder (!panel-setup)'}</span>
                  </button>
                  <button
                    onClick={() => {
                      setPanelConfig(defaultScreenshotConfig);
                      setTempConfig(defaultScreenshotConfig);
                    }}
                    className="px-2.5 py-1 text-xs font-medium bg-[#2b2d31] hover:bg-[#35373c] text-[#b5bac1] rounded transition-colors cursor-pointer"
                    title="Reset to Screenshot Defaults"
                  >
                    <span>🔄 Reset</span>
                  </button>
                </div>
              </div>

              {/* Official Ticket Panel Control Dashboard (Exact Match to Screenshot 2) */}
              {showBuilderDashboard && (
                <div className="bg-[#2b2d31] rounded-2xl border border-[#1f2023] p-5 shadow-2xl max-w-lg mx-auto space-y-3 animate-fade-in">
                  {/* Header Block matching Screenshot 2 */}
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xl">📚</span>
                        <h3 className="text-base font-bold text-white tracking-wide">Ticket Panel</h3>
                      </div>
                      <div className="text-xs text-[#dbdee1] space-y-0.5">
                        <div>
                          Status: <span className={panelConfig.is_active ? 'text-emerald-400 font-semibold' : 'text-red-400 font-semibold'}>
                            {panelConfig.is_active ? 'Active' : 'Disabled'}
                          </span>
                        </div>
                        <div>
                          Categories: <span className="text-white font-medium">5/5 active</span>
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => setShowBuilderDashboard(false)}
                      className="text-[#949ba4] hover:text-white text-xs cursor-pointer px-2 py-1 bg-[#1e1f22] rounded border border-[#383a40]"
                    >
                      ✕ Close
                    </button>
                  </div>

                  <div className="border-t border-[#383a40] my-2" />

                  {/* Button Rows Matching Screenshot 2 Exactly */}
                  <div className="space-y-2">
                    {/* Row 0: [Edit Name] [Edit Message] */}
                    <div className="flex gap-2">
                      <button
                        onClick={() => {
                          setTempConfig({ ...panelConfig });
                          setActiveBuilderModal('header');
                        }}
                        className="flex-1 px-4 py-2 text-xs font-semibold bg-[#35373c] hover:bg-[#404249] text-white rounded transition-colors cursor-pointer"
                      >
                        Edit Name
                      </button>
                      <button
                        onClick={() => {
                          setTempConfig({ ...panelConfig });
                          setActiveBuilderModal('intro');
                        }}
                        className="flex-1 px-4 py-2 text-xs font-semibold bg-[#35373c] hover:bg-[#404249] text-white rounded transition-colors cursor-pointer"
                      >
                        Edit Message
                      </button>
                    </div>

                    {/* Row 1: [Edit Placeholder] */}
                    <div className="flex gap-2">
                      <button
                        onClick={() => {
                          setTempConfig({ ...panelConfig });
                          setActiveBuilderModal('header');
                        }}
                        className="flex-1 px-4 py-2 text-xs font-semibold bg-[#35373c] hover:bg-[#404249] text-white rounded transition-colors cursor-pointer"
                      >
                        Edit Placeholder
                      </button>
                    </div>

                    {/* Row 2: [Disable Panel] [Manage Categories] */}
                    <div className="flex gap-2">
                      <button
                        onClick={() => {
                          setPanelConfig({ ...panelConfig, is_active: !panelConfig.is_active });
                          setSecurityNotice(`Panel Status changed to: ${!panelConfig.is_active ? 'Active' : 'Disabled'}`);
                          setTimeout(() => setSecurityNotice(null), 4000);
                        }}
                        className={`flex-1 px-4 py-2 text-xs font-semibold text-white rounded transition-colors cursor-pointer ${
                          panelConfig.is_active
                            ? 'bg-red-600 hover:bg-red-500'
                            : 'bg-emerald-600 hover:bg-emerald-500'
                        }`}
                      >
                        {panelConfig.is_active ? 'Disable Panel' : 'Enable Panel'}
                      </button>
                      <button
                        onClick={() => {
                          setTempConfig({ ...panelConfig });
                          setActiveBuilderModal('categories');
                        }}
                        className="flex-1 px-4 py-2 text-xs font-semibold bg-[#5865F2] hover:bg-[#4752c4] text-white rounded transition-colors cursor-pointer"
                      >
                        Manage Categories
                      </button>
                    </div>

                    {/* Row 3: [Configure Logs] */}
                    <div className="flex gap-2">
                      <button
                        onClick={() => {
                          setTempConfig({ ...panelConfig });
                          setActiveBuilderModal('footer');
                        }}
                        className="flex-1 px-4 py-2 text-xs font-semibold bg-[#5865F2] hover:bg-[#4752c4] text-white rounded transition-colors cursor-pointer"
                      >
                        Configure Logs
                      </button>
                    </div>

                    {/* Row 4: [Send Panel] [Delete Panel] */}
                    <div className="flex gap-2">
                      <button
                        onClick={() => {
                          setSecurityNotice('✅ Support Ticket Panel Sent & Published to #1. create-a-ticket.!');
                          setTimeout(() => setSecurityNotice(null), 5000);
                          setShowBuilderDashboard(false);
                        }}
                        className="flex-1 px-4 py-2 text-xs font-semibold bg-[#23a55a] hover:bg-[#1f9250] text-white rounded transition-colors cursor-pointer"
                      >
                        Send Panel
                      </button>
                      <button
                        onClick={() => {
                          setPanelConfig(defaultScreenshotConfig);
                          setTempConfig(defaultScreenshotConfig);
                          setSecurityNotice('🔄 Ticket Panel Reset to Factory Defaults');
                          setTimeout(() => setSecurityNotice(null), 5000);
                        }}
                        className="flex-1 px-4 py-2 text-xs font-semibold bg-red-600 hover:bg-red-500 text-white rounded transition-colors cursor-pointer"
                      >
                        Delete Panel
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Official HelzerX Support Panel (Container V2 Style - NO SIDE COLOR LINE) */}
              <div className="bg-[#2b2d31] rounded-2xl border border-[#1f2023] p-6 shadow-2xl space-y-4">
                {/* 1. Top Logo (Metallic Chrome 3D Logo) */}
                <div className="flex justify-center py-2">
                  <img
                    src={panelConfig.topLogoUrl || '/assets/helzerx-logo-3d.png'}
                    alt="HelzerX"
                    className="h-16 max-w-full object-contain filter drop-shadow-md"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = '/assets/helzerx-logo-3d.png';
                    }}
                  />
                </div>

                <div className="border-t border-[#383a40]" />

                {/* 2. Header & Title */}
                <h2 className="text-center font-bold text-white text-lg sm:text-xl tracking-wide">
                  {panelConfig.title}
                </h2>

                <div className="border-t border-[#383a40]" />

                {/* 3. Intro Description */}
                <p className="text-xs sm:text-sm text-[#dbdee1] leading-relaxed whitespace-pre-wrap">
                  {panelConfig.description}
                </p>

                <div className="border-t border-[#383a40]" />

                {/* 4. Support Categories Section */}
                <div>
                  <div className="text-xs font-bold text-white underline mb-2 tracking-wide">
                    {panelConfig.categoriesTitle}
                  </div>
                  <div className="text-xs text-[#dbdee1] space-y-1.5 whitespace-pre-wrap leading-relaxed pl-1">
                    {panelConfig.categoriesList}
                  </div>
                </div>

                <div className="border-t border-[#383a40]" />

                {/* 5. Please Note Section */}
                <div>
                  <div className="text-xs font-bold text-white flex items-center gap-1.5">
                    <span className="text-[#80848e]">ℹ️</span>
                    <span>{panelConfig.noteTitle}</span>
                  </div>
                  <p className="text-xs text-[#b5bac1] mt-1 leading-relaxed">
                    {panelConfig.noteText}
                  </p>
                </div>

                <div className="border-t border-[#383a40]" />

                {/* 6. Bottom Banner (Cosmic Space HelzerX Support Banner) */}
                <div className="rounded-lg overflow-hidden border border-[#1f2023] bg-black/40 my-2">
                  <img
                    src={panelConfig.bannerUrl || '/assets/helzerx-banner.png'}
                    alt="HelzerX Support"
                    className="w-full object-cover max-h-56"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = '/assets/helzerx-banner.png';
                    }}
                  />
                </div>

                <div className="border-t border-[#383a40]" />

                {/* 7. Footer Attribution */}
                <div className="text-[11px] text-[#80848e] space-y-0.5">
                  <p className="font-semibold text-[#949ba4]">{panelConfig.footerLine1}</p>
                  <p className="italic">{panelConfig.footerLine2}</p>
                </div>

                <div className="border-t border-[#383a40]" />

                {/* 8. Dropdown Select Menu Component */}
                <div className="pt-1">
                  <label className="block text-[11px] font-semibold text-[#80848e] mb-1.5 uppercase tracking-wider">
                    {panelConfig.selectPlaceholder}
                  </label>
                  <select
                    value={modalCategory}
                    onChange={e => {
                      setModalCategory(e.target.value);
                      setShowCreateModal(true);
                    }}
                    className="w-full bg-[#1e1f22] border border-[#3f4147] rounded-lg px-3.5 py-3 text-xs text-white focus:outline-none focus:border-indigo-500 cursor-pointer"
                  >
                    <option value="" disabled>{panelConfig.selectPlaceholder}...</option>
                    {TICKET_CATEGORIES.map(cat => (
                      <option key={cat.id} value={cat.id}>
                        {cat.emoji} {cat.name} — {cat.description}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          )}

          {selectedChannel !== 'create-a-ticket' && activeTicket && (
            <div className="space-y-4 max-w-4xl mx-auto">
              {/* Ticket Welcome Embed (Components V2 Container - NO SIDE COLOR LINE) */}
              <div className="bg-[#2b2d31] rounded-xl border border-[#1f2023] p-4 space-y-3 shadow-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-base">Ticket {activeTicket.code}</span>
                    <span className="text-xs text-[#949ba4]">· {activeTicket.categoryName}</span>
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded font-mono font-bold ${
                    activeTicket.priority === 'URGENT'
                      ? 'bg-red-950 text-red-400 border border-red-800'
                      : activeTicket.priority === 'HIGH'
                      ? 'bg-amber-950 text-amber-400 border border-amber-800'
                      : 'bg-slate-800 text-slate-300'
                  }`}>
                    {activeTicket.priority}
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs text-[#b5bac1]">
                  <div>
                    <span className="text-[#80848e] block">Creator</span>
                    <span className="font-medium text-white">{activeTicket.creator}</span>
                  </div>
                  <div>
                    <span className="text-[#80848e] block">Status</span>
                    <span className="font-medium text-white">{activeTicket.status}</span>
                  </div>
                  <div>
                    <span className="text-[#80848e] block">Assignee</span>
                    <span className="font-medium text-white">{activeTicket.claimedBy || 'Unassigned'}</span>
                  </div>
                  {activeTicket.serverIdentifier && (
                    <div className="col-span-2">
                      <span className="text-[#80848e] block">Service / Node</span>
                      <code className="text-indigo-300 font-mono text-[11px]">{activeTicket.serverIdentifier}</code>
                    </div>
                  )}
                </div>

                {/* In-Ticket Control Buttons */}
                <div className="pt-2 border-t border-[#35373c] flex flex-wrap gap-2">
                  <button
                    onClick={() => onClaimTicket(activeTicket.id, isStaffMode ? 'SupportEngineer' : 'Staff_Devon')}
                    disabled={Boolean(activeTicket.claimedBy)}
                    className={`px-3 py-1.5 text-xs rounded font-medium flex items-center gap-1.5 transition-colors cursor-pointer ${
                      activeTicket.claimedBy
                        ? 'bg-[#1e1f22] text-[#80848e] cursor-not-allowed'
                        : 'bg-indigo-600 hover:bg-indigo-500 text-white'
                    }`}
                  >
                    <UserCheck className="w-3.5 h-3.5" />
                    <span>{activeTicket.claimedBy ? `Claimed by ${activeTicket.claimedBy}` : 'Claim Ticket'}</span>
                  </button>

                  <button
                    onClick={() => onEscalateTicket(activeTicket.id, 'Customer requested human support')}
                    className="px-3 py-1.5 text-xs rounded font-medium bg-[#35373c] hover:bg-[#404249] text-white flex items-center gap-1.5 transition-colors cursor-pointer"
                  >
                    <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                    <span>Request Human Staff</span>
                  </button>

                  {isStaffMode && (
                    <button
                      onClick={() => setShowNoteModal(true)}
                      className="px-3 py-1.5 text-xs rounded font-medium bg-[#35373c] hover:bg-[#404249] text-white flex items-center gap-1.5 transition-colors cursor-pointer"
                    >
                      <Lock className="w-3.5 h-3.5 text-amber-400" />
                      <span>Internal Note</span>
                    </button>
                  )}

                  <button
                    onClick={() => handleDownloadTranscript(activeTicket)}
                    className="px-3 py-1.5 text-xs rounded font-medium bg-[#35373c] hover:bg-[#404249] text-white flex items-center gap-1.5 transition-colors cursor-pointer"
                  >
                    <FileText className="w-3.5 h-3.5 text-sky-400" />
                    <span>Transcript</span>
                  </button>

                  <button
                    onClick={() => setShowCloseConfirm(true)}
                    className="px-3 py-1.5 text-xs rounded font-medium bg-red-600 hover:bg-red-500 text-white flex items-center gap-1.5 transition-colors cursor-pointer ml-auto"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    <span>Close Ticket</span>
                  </button>
                </div>
              </div>

              {/* Staff-Only Internal Notes Box (Hidden when in Customer Mode) */}
              {isStaffMode && activeTicket.internalNotes.length > 0 && (
                <div className="bg-amber-950/30 border border-amber-900/60 rounded-lg p-3 space-y-2">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-amber-300">
                    <Lock className="w-3.5 h-3.5" />
                    <span>Confidential Internal Notes (Staff Only • Invisible to Customer)</span>
                  </div>
                  {activeTicket.internalNotes.map(n => (
                    <div key={n.id} className="text-xs text-amber-200/90 pl-3 border-l-2 border-amber-600">
                      <span className="font-semibold text-amber-100">{n.author}</span>
                      <span className="text-[10px] text-amber-400/70 ml-2">{n.timestamp}</span>
                      <p className="mt-0.5 whitespace-pre-wrap">{n.content}</p>
                    </div>
                  ))}
                </div>
              )}

              {/* Messages Feed (Plain Text Chat - NO SIDE COLOR LINE) */}
              {activeTicket.messages.map(m => {
                const isAi = m.authorRole === 'ai';
                const isStaff = m.authorRole === 'staff';

                return (
                  <div
                    key={m.id}
                    className="flex gap-3 px-2 py-1.5 rounded hover:bg-[#2e3035] transition-colors"
                  >
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm shrink-0 ${
                        isAi
                          ? 'bg-indigo-600 text-white'
                          : isStaff
                          ? 'bg-emerald-600 text-white'
                          : 'bg-[#4752c4] text-white'
                      }`}
                    >
                      {isAi ? <Cpu className="w-5 h-5" /> : m.authorName.slice(0, 2).toUpperCase()}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-white text-sm">{m.authorName}</span>
                        {isAi && (
                          <span className="bg-indigo-600 text-white text-[10px] font-bold px-1.5 py-0.2 rounded">
                            HELZERX AI
                          </span>
                        )}
                        {isStaff && (
                          <span className="bg-emerald-600 text-white text-[10px] font-bold px-1.5 py-0.2 rounded">
                            STAFF
                          </span>
                        )}
                        <span className="text-[11px] text-[#949ba4]">{m.timestamp}</span>
                        {m.latencyMs && (
                          <span className="text-[10px] text-indigo-300 font-mono">
                            {m.latencyMs}ms
                          </span>
                        )}
                        {m.detectedLang === 'singlish' && (
                          <span className="text-[10px] text-amber-400 font-mono">
                            Singlish
                          </span>
                        )}
                      </div>

                      <div className="text-sm text-[#dbdee1] mt-1 whitespace-pre-wrap leading-relaxed">
                        {m.content}
                      </div>
                    </div>
                  </div>
                );
              })}

              {/* AI Typing Indicator */}
              {isAiTyping && (
                <div className="flex items-center gap-2 px-3 py-2 text-xs text-indigo-300 italic">
                  <div className="flex gap-1">
                    <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" />
                    <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                    <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.4s]" />
                  </div>
                  <span>HELZERX AI Support is typing an expert solution...</span>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Message Input Bar */}
        {selectedChannel === 'create-a-ticket' ? (
          <div className="p-4 bg-[#313338] border-t border-[#232428] shrink-0">
            <div className="bg-[#383a40] rounded-lg px-4 py-2.5 flex items-center gap-3">
              <input
                type="text"
                value={inputMessage}
                onChange={e => setInputMessage(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSendMessage()}
                placeholder="Type !panel-setup to launch Container Builder, or select a department above..."
                className="flex-1 bg-transparent text-sm text-white placeholder-[#80848e] focus:outline-none"
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim()}
                className={`p-1.5 rounded-md transition-colors cursor-pointer ${
                  inputMessage.trim()
                    ? 'bg-indigo-600 text-white hover:bg-indigo-500'
                    : 'text-[#80848e] cursor-not-allowed'
                }`}
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
            <div className="flex items-center justify-between text-[11px] text-[#949ba4] px-1 mt-1.5">
              <span>Admin commands: <code>!panel-setup</code> • <code>!panel</code> • <code>!sync</code></span>
              <span>HelzerX Support Engine Active</span>
            </div>
          </div>
        ) : activeTicket && (
          <div className="p-4 bg-[#313338] border-t border-[#232428] shrink-0">
            <div className="bg-[#383a40] rounded-lg px-4 py-2.5 flex items-center gap-3">
              <input
                type="text"
                value={inputMessage}
                onChange={e => setInputMessage(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSendMessage()}
                placeholder={
                  isStaffMode
                    ? `Reply as HELZERX Staff in #${activeTicket.code.toLowerCase()}...`
                    : `Message #${activeTicket.code.toLowerCase()} (English, Sinhala, Singlish)...`
                }
                className="flex-1 bg-transparent text-sm text-white placeholder-[#80848e] focus:outline-none"
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim()}
                className={`p-1.5 rounded-md transition-colors cursor-pointer ${
                  inputMessage.trim()
                    ? 'bg-indigo-600 text-white hover:bg-indigo-500'
                    : 'text-[#80848e] cursor-not-allowed'
                }`}
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
            <div className="flex items-center justify-between text-[11px] text-[#949ba4] px-1 mt-1.5">
              <span>Trilingual: Type in <strong>English</strong>, <strong>Sinhala (සිංහල)</strong>, or <strong>Singlish</strong></span>
              <span>Protected by HELZERX Security Guard & Regex Sanitizer</span>
            </div>
          </div>
        )}
      </div>

      {/* Modal: Create Ticket */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-[#313338] border border-[#232428] rounded-xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-[#232428] pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>Create Support Ticket</span>
              </h3>
              <button onClick={() => setShowCreateModal(false)} className="text-[#80848e] hover:text-white cursor-pointer">
                ✕
              </button>
            </div>

            <div className="space-y-3 text-sm">
              <div>
                <label className="block text-xs font-semibold text-[#b5bac1] mb-1">Department</label>
                <select
                  value={modalCategory}
                  onChange={e => setModalCategory(e.target.value)}
                  className="w-full bg-[#1e1f22] border border-[#3f4147] rounded-md px-3 py-2 text-white"
                >
                  {TICKET_CATEGORIES.map(c => (
                    <option key={c.id} value={c.id}>{c.emoji} {c.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#b5bac1] mb-1">Brief Summary of the Issue *</label>
                <input
                  type="text"
                  value={modalSubject}
                  onChange={e => setModalSubject(e.target.value)}
                  placeholder="e.g. Server crashed after updating Paper jar"
                  className="w-full bg-[#1e1f22] border border-[#3f4147] rounded-md px-3 py-2 text-white placeholder-[#80848e]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#b5bac1] mb-1">Detailed Description & Error Logs *</label>
                <textarea
                  rows={4}
                  value={modalDesc}
                  onChange={e => setModalDesc(e.target.value)}
                  placeholder="Describe what occurred, error logs, or symptoms (English, Sinhala, Singlish)..."
                  className="w-full bg-[#1e1f22] border border-[#3f4147] rounded-md px-3 py-2 text-white placeholder-[#80848e] font-sans"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#b5bac1] mb-1">Service Identifier, Node or IP (Optional)</label>
                <input
                  type="text"
                  value={modalServerId}
                  onChange={e => setModalServerId(e.target.value)}
                  placeholder="e.g. node-02 / srv-88421 or play.example.com"
                  className="w-full bg-[#1e1f22] border border-[#3f4147] rounded-md px-3 py-2 text-white placeholder-[#80848e]"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-[#232428]">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 text-xs font-semibold text-[#dbdee1] hover:underline cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (!modalSubject.trim() || !modalDesc.trim()) return;
                  onCreateTicket(modalCategory, modalSubject, modalDesc, modalServerId);
                  setShowCreateModal(false);
                  setModalSubject('');
                  setModalDesc('');
                  setModalServerId('');
                }}
                disabled={!modalSubject.trim() || !modalDesc.trim()}
                className="px-5 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-md transition-colors cursor-pointer disabled:opacity-50"
              >
                Submit Ticket
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Internal Note */}
      {showNoteModal && activeTicket && (
        <div className="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-[#313338] border border-[#232428] rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Lock className="w-4 h-4 text-amber-400" />
              <span>Add Confidential Staff Note</span>
            </h3>
            <p className="text-xs text-[#949ba4]">
              Internal notes are recorded strictly for support engineers and will <strong>never</strong> be visible to the customer.
            </p>
            <textarea
              rows={4}
              value={internalNoteText}
              onChange={e => setInternalNoteText(e.target.value)}
              placeholder="e.g. Verified node CPU wait is normal. Suspect faulty custom plugin on customer container..."
              className="w-full bg-[#1e1f22] border border-[#3f4147] rounded-md p-3 text-sm text-white placeholder-[#80848e]"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowNoteModal(false)}
                className="px-4 py-2 text-xs font-semibold text-[#dbdee1] hover:underline cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (!internalNoteText.trim()) return;
                  onAddInternalNote(activeTicket.id, internalNoteText, 'SupportEngineer');
                  setInternalNoteText('');
                  setShowNoteModal(false);
                }}
                className="px-4 py-2 text-xs font-semibold text-white bg-amber-600 hover:bg-amber-500 rounded-md cursor-pointer"
              >
                Save Internal Note
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Confirm Close */}
      {showCloseConfirm && activeTicket && (
        <div className="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-[#313338] border border-[#232428] rounded-xl max-w-sm w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <XCircle className="w-5 h-5 text-red-500" />
              <span>Close Ticket {activeTicket.code}?</span>
            </h3>
            <p className="text-xs text-[#b5bac1]">
              Marking this ticket as closed will archive all messages and generate the final HTML transcript.
            </p>
            <input
              type="text"
              value={closeReason}
              onChange={e => setCloseReason(e.target.value)}
              placeholder="Closure reason (e.g. Resolved by customer)"
              className="w-full bg-[#1e1f22] border border-[#3f4147] rounded-md px-3 py-2 text-sm text-white placeholder-[#80848e]"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowCloseConfirm(false)}
                className="px-4 py-2 text-xs font-semibold text-[#dbdee1] hover:underline cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  onCloseTicket(activeTicket.id, closeReason || 'Resolved');
                  setShowCloseConfirm(false);
                  setCloseReason('');
                }}
                className="px-4 py-2 text-xs font-semibold text-white bg-red-600 hover:bg-red-500 rounded-md cursor-pointer"
              >
                Confirm & Archive
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modular Builder Modal: Header & Title */}
      {activeBuilderModal === 'header' && (
        <div className="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-[#313338] border border-[#232428] rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-2 border-b border-[#232428]">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span>✏️ Edit Header & Dropdown Placeholder</span>
              </h3>
              <button onClick={() => setActiveBuilderModal(null)} className="text-[#949ba4] hover:text-white text-sm cursor-pointer">✕</button>
            </div>
            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-[#b5bac1] font-semibold mb-1">Container Title</label>
                <input
                  type="text"
                  value={tempConfig.title}
                  onChange={e => setTempConfig({ ...tempConfig, title: e.target.value })}
                  placeholder="e.g. 🎧 HelzerX Support Center 🎧"
                  className="w-full bg-[#1e1f22] border border-[#3f4147] rounded-md px-3 py-2 text-white"
                />
              </div>
              <div>
                <label className="block text-[#b5bac1] font-semibold mb-1">Dropdown Component Placeholder</label>
                <input
                  type="text"
                  value={tempConfig.selectPlaceholder}
                  onChange={e => setTempConfig({ ...tempConfig, selectPlaceholder: e.target.value })}
                  placeholder="Select a ticket category"
                  className="w-full bg-[#1e1f22] border border-[#3f4147] rounded-md px-3 py-2 text-white"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2 border-t border-[#232428]">
              <button onClick={() => setActiveBuilderModal(null)} className="px-3 py-1.5 text-xs text-[#b5bac1] hover:underline cursor-pointer">Cancel</button>
              <button
                onClick={() => {
                  setPanelConfig({ ...panelConfig, title: tempConfig.title, selectPlaceholder: tempConfig.selectPlaceholder });
                  setActiveBuilderModal(null);
                }}
                className="px-4 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-md cursor-pointer"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modular Builder Modal: Intro Text */}
      {activeBuilderModal === 'intro' && (
        <div className="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-[#313338] border border-[#232428] rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-2 border-b border-[#232428]">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span>📝 Edit Intro & Subtitle Description</span>
              </h3>
              <button onClick={() => setActiveBuilderModal(null)} className="text-[#949ba4] hover:text-white text-sm cursor-pointer">✕</button>
            </div>
            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-[#b5bac1] font-semibold mb-1">Intro Text</label>
                <textarea
                  rows={4}
                  value={tempConfig.description}
                  onChange={e => setTempConfig({ ...tempConfig, description: e.target.value })}
                  placeholder="Need assistance? Our support team is here to help..."
                  className="w-full bg-[#1e1f22] border border-[#3f4147] rounded-md px-3 py-2 text-white"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2 border-t border-[#232428]">
              <button onClick={() => setActiveBuilderModal(null)} className="px-3 py-1.5 text-xs text-[#b5bac1] hover:underline cursor-pointer">Cancel</button>
              <button
                onClick={() => {
                  setPanelConfig({ ...panelConfig, description: tempConfig.description });
                  setActiveBuilderModal(null);
                }}
                className="px-4 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-md cursor-pointer"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modular Builder Modal: Categories */}
      {activeBuilderModal === 'categories' && (
        <div className="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-[#313338] border border-[#232428] rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-2 border-b border-[#232428]">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span>📋 Edit Support Categories Section</span>
              </h3>
              <button onClick={() => setActiveBuilderModal(null)} className="text-[#949ba4] hover:text-white text-sm cursor-pointer">✕</button>
            </div>
            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-[#b5bac1] font-semibold mb-1">Section Heading</label>
                <input
                  type="text"
                  value={tempConfig.categoriesTitle}
                  onChange={e => setTempConfig({ ...tempConfig, categoriesTitle: e.target.value })}
                  placeholder="Support Categories"
                  className="w-full bg-[#1e1f22] border border-[#3f4147] rounded-md px-3 py-2 text-white"
                />
              </div>
              <div>
                <label className="block text-[#b5bac1] font-semibold mb-1">Categories Bullet List</label>
                <textarea
                  rows={5}
                  value={tempConfig.categoriesList}
                  onChange={e => setTempConfig({ ...tempConfig, categoriesList: e.target.value })}
                  placeholder="• 👥 General Support..."
                  className="w-full bg-[#1e1f22] border border-[#3f4147] rounded-md px-3 py-2 text-white font-mono"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2 border-t border-[#232428]">
              <button onClick={() => setActiveBuilderModal(null)} className="px-3 py-1.5 text-xs text-[#b5bac1] hover:underline cursor-pointer">Cancel</button>
              <button
                onClick={() => {
                  setPanelConfig({ ...panelConfig, categoriesTitle: tempConfig.categoriesTitle, categoriesList: tempConfig.categoriesList });
                  setActiveBuilderModal(null);
                }}
                className="px-4 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-md cursor-pointer"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modular Builder Modal: Note Section */}
      {activeBuilderModal === 'note' && (
        <div className="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-[#313338] border border-[#232428] rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-2 border-b border-[#232428]">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span>ℹ️ Edit Please Note Box</span>
              </h3>
              <button onClick={() => setActiveBuilderModal(null)} className="text-[#949ba4] hover:text-white text-sm cursor-pointer">✕</button>
            </div>
            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-[#b5bac1] font-semibold mb-1">Note Heading</label>
                <input
                  type="text"
                  value={tempConfig.noteTitle}
                  onChange={e => setTempConfig({ ...tempConfig, noteTitle: e.target.value })}
                  placeholder="Please Note"
                  className="w-full bg-[#1e1f22] border border-[#3f4147] rounded-md px-3 py-2 text-white"
                />
              </div>
              <div>
                <label className="block text-[#b5bac1] font-semibold mb-1">Note Description</label>
                <textarea
                  rows={3}
                  value={tempConfig.noteText}
                  onChange={e => setTempConfig({ ...tempConfig, noteText: e.target.value })}
                  placeholder="Submit one ticket per issue..."
                  className="w-full bg-[#1e1f22] border border-[#3f4147] rounded-md px-3 py-2 text-white"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2 border-t border-[#232428]">
              <button onClick={() => setActiveBuilderModal(null)} className="px-3 py-1.5 text-xs text-[#b5bac1] hover:underline cursor-pointer">Cancel</button>
              <button
                onClick={() => {
                  setPanelConfig({ ...panelConfig, noteTitle: tempConfig.noteTitle, noteText: tempConfig.noteText });
                  setActiveBuilderModal(null);
                }}
                className="px-4 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-md cursor-pointer"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modular Builder Modal: Top Logo & Bottom Banner */}
      {activeBuilderModal === 'images' && (
        <div className="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-[#313338] border border-[#232428] rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-2 border-b border-[#232428]">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span>🖼️ Configure Top Logo & Bottom Banner</span>
              </h3>
              <button onClick={() => setActiveBuilderModal(null)} className="text-[#949ba4] hover:text-white text-sm cursor-pointer">✕</button>
            </div>
            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-[#b5bac1] font-semibold mb-1">Top Metallic Logo Image URL</label>
                <input
                  type="text"
                  value={tempConfig.topLogoUrl}
                  onChange={e => setTempConfig({ ...tempConfig, topLogoUrl: e.target.value })}
                  placeholder="/assets/helzerx-logo-3d.png or https://..."
                  className="w-full bg-[#1e1f22] border border-[#3f4147] rounded-md px-3 py-2 text-white"
                />
              </div>
              <div>
                <label className="block text-[#b5bac1] font-semibold mb-1">Bottom Space Banner URL</label>
                <input
                  type="text"
                  value={tempConfig.bannerUrl}
                  onChange={e => setTempConfig({ ...tempConfig, bannerUrl: e.target.value })}
                  placeholder="/assets/helzerx-banner.png or https://..."
                  className="w-full bg-[#1e1f22] border border-[#3f4147] rounded-md px-3 py-2 text-white"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2 border-t border-[#232428]">
              <button onClick={() => setActiveBuilderModal(null)} className="px-3 py-1.5 text-xs text-[#b5bac1] hover:underline cursor-pointer">Cancel</button>
              <button
                onClick={() => {
                  setPanelConfig({ ...panelConfig, topLogoUrl: tempConfig.topLogoUrl, bannerUrl: tempConfig.bannerUrl });
                  setActiveBuilderModal(null);
                }}
                className="px-4 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-md cursor-pointer"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modular Builder Modal: Footer Attribution */}
      {activeBuilderModal === 'footer' && (
        <div className="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-[#313338] border border-[#232428] rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-2 border-b border-[#232428]">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span>🏷️ Edit Footer Attribution</span>
              </h3>
              <button onClick={() => setActiveBuilderModal(null)} className="text-[#949ba4] hover:text-white text-sm cursor-pointer">✕</button>
            </div>
            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-[#b5bac1] font-semibold mb-1">Company Title (Line 1)</label>
                <input
                  type="text"
                  value={tempConfig.footerLine1}
                  onChange={e => setTempConfig({ ...tempConfig, footerLine1: e.target.value })}
                  placeholder="HelzerX Technologies"
                  className="w-full bg-[#1e1f22] border border-[#3f4147] rounded-md px-3 py-2 text-white"
                />
              </div>
              <div>
                <label className="block text-[#b5bac1] font-semibold mb-1">Copyright Attribution (Line 2)</label>
                <input
                  type="text"
                  value={tempConfig.footerLine2}
                  onChange={e => setTempConfig({ ...tempConfig, footerLine2: e.target.value })}
                  placeholder="© 2026 HelzerX Technologies (Pvt) Ltd. All rights reserved."
                  className="w-full bg-[#1e1f22] border border-[#3f4147] rounded-md px-3 py-2 text-white"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2 border-t border-[#232428]">
              <button onClick={() => setActiveBuilderModal(null)} className="px-3 py-1.5 text-xs text-[#b5bac1] hover:underline cursor-pointer">Cancel</button>
              <button
                onClick={() => {
                  setPanelConfig({ ...panelConfig, footerLine1: tempConfig.footerLine1, footerLine2: tempConfig.footerLine2 });
                  setActiveBuilderModal(null);
                }}
                className="px-4 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-md cursor-pointer"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
