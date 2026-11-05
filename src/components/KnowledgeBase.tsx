import React, { useState } from 'react';
import { KNOWLEDGE_DOCS } from '../data/defaultData';
import { BookOpen, Search, PlusCircle, CheckCircle, Tag, FileText, ArrowRight } from 'lucide-react';

export const KnowledgeBase: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedDocId, setSelectedDocId] = useState<string>(KNOWLEDGE_DOCS[0].id);
  const [showAddModal, setShowAddModal] = useState<boolean>(false);
  const [newTitle, setNewTitle] = useState<string>('');
  const [newCategory, setNewCategory] = useState<string>('technical');
  const [newContent, setNewContent] = useState<string>('');
  const [newTags, setNewTags] = useState<string>('');
  const [docsList, setDocsList] = useState(KNOWLEDGE_DOCS);

  // Compute live RAG score simulation
  const scoreDoc = (doc: typeof KNOWLEDGE_DOCS[0], q: string): number => {
    if (!q.trim()) return 1.0;
    const queryTerms = q.toLowerCase().split(/\s+/).filter(Boolean);
    let score = 0;
    const titleLower = doc.title.toLowerCase();
    const contentLower = doc.content.toLowerCase();
    const catLower = doc.category.toLowerCase();

    queryTerms.forEach(term => {
      if (titleLower.includes(term)) score += 4.5;
      if (catLower.includes(term)) score += 2.0;
      if (doc.tags.some(t => t.toLowerCase().includes(term))) score += 3.0;
      const count = (contentLower.match(new RegExp(term, 'g')) || []).length;
      if (count > 0) score += Math.min(6, 1 + Math.log2(count));
    });

    return Math.round(score * 10) / 10;
  };

  const filteredDocs = docsList
    .map(doc => ({
      ...doc,
      score: scoreDoc(doc, searchQuery)
    }))
    .filter(doc => {
      const matchesCat = selectedCategory === 'all' || doc.category === selectedCategory;
      const matchesSearch = !searchQuery.trim() || doc.score > 0;
      return matchesCat && matchesSearch;
    })
    .sort((a, b) => b.score - a.score);

  const selectedDoc = docsList.find(d => d.id === selectedDocId) || docsList[0];

  const handleAddDoc = () => {
    if (!newTitle.trim() || !newContent.trim()) return;
    const newDoc = {
      id: `k-${Date.now()}`,
      title: newTitle,
      category: newCategory,
      tags: newTags.split(',').map(t => t.trim()).filter(Boolean),
      summary: newContent.slice(0, 100) + '...',
      content: newContent
    };
    setDocsList([newDoc, ...docsList]);
    setSelectedDocId(newDoc.id);
    setShowAddModal(false);
    setNewTitle('');
    setNewContent('');
    setNewTags('');
  };

  return (
    <div className="h-full flex flex-col bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Top Search & Filter Bar */}
      <div className="p-6 bg-slate-900 border-b border-slate-800 shrink-0">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-indigo-400" />
              <h1 className="text-lg font-bold text-white tracking-tight">
                Verified HELZERX Knowledge Base & RAG Index
              </h1>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Indexed documentation retrieved during automated ticket triage to provide grounded step-by-step diagnostic reasoning.
            </p>
          </div>

          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-lg flex items-center gap-2 transition-colors cursor-pointer shrink-0"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Add Documentation</span>
          </button>
        </div>

        {/* Search Input & Category Filters */}
        <div className="flex flex-col md:flex-row items-stretch md:items-center gap-3 mt-4">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder="Test RAG Query Search (e.g. 'oom error', 'wings ehostunreach', 'orange cloud srv', 'refund')..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="flex items-center gap-1.5 overflow-x-auto text-xs py-1">
            {['all', 'minecraft', 'technical', 'vps', 'dedicated', 'billing'].map(cat => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1.5 rounded-md font-medium capitalize whitespace-nowrap transition-colors cursor-pointer ${
                  selectedCategory === cat
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main 2-Column Split: Document List + Document Reader */}
      <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
        {/* Left Column: Search & Ranked Results */}
        <div className="w-full md:w-96 border-r border-slate-800 bg-slate-900/60 overflow-y-auto p-4 space-y-2.5 shrink-0">
          <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 px-1 flex items-center justify-between">
            <span>Indexed Guides ({filteredDocs.length})</span>
            {searchQuery && <span className="text-indigo-400 font-mono">Ranked by BM25 Score</span>}
          </div>

          {filteredDocs.map(doc => {
            const isSelected = doc.id === selectedDocId;
            return (
              <div
                key={doc.id}
                onClick={() => setSelectedDocId(doc.id)}
                className={`p-3.5 rounded-lg border text-left cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-indigo-950/40 border-indigo-500/80 shadow-xs'
                    : 'bg-slate-900 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="font-semibold text-white truncate max-w-[200px]">
                    {doc.title}
                  </span>
                  {searchQuery && (
                    <span className="font-mono text-[10px] text-emerald-400 font-bold bg-emerald-950/80 px-1.5 py-0.5 rounded border border-emerald-800/80">
                      Score: {doc.score}
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                  {doc.summary}
                </p>
                <div className="flex items-center gap-1.5 mt-2.5 flex-wrap">
                  <span className="text-[10px] uppercase font-bold text-indigo-300 bg-indigo-950 px-1.5 py-0.5 rounded">
                    {doc.category}
                  </span>
                  {doc.tags.slice(0, 3).map(tag => (
                    <span key={tag} className="text-[10px] text-slate-400 font-mono">
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column: Full Markdown Content Viewport */}
        <div className="flex-1 overflow-y-auto p-6 bg-slate-950">
          {selectedDoc ? (
            <div className="max-w-3xl mx-auto space-y-4">
              <div className="border-b border-slate-800 pb-4">
                <div className="flex items-center gap-2 text-xs text-indigo-400 font-semibold uppercase tracking-wider mb-1">
                  <span>{selectedDoc.category}</span>
                  <span>·</span>
                  <span className="text-emerald-400 flex items-center gap-1">
                    <CheckCircle className="w-3.5 h-3.5" />
                    Verified HELZERX Documentation
                  </span>
                </div>
                <h2 className="text-xl font-bold text-white tracking-tight">
                  {selectedDoc.title}
                </h2>
                <div className="flex items-center gap-2 mt-2 text-xs text-slate-400">
                  <Tag className="w-3.5 h-3.5" />
                  <span>Tags: {selectedDoc.tags.join(', ')}</span>
                </div>
              </div>

              {/* Formatted Content */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 text-sm text-slate-200 leading-relaxed font-sans space-y-4">
                <pre className="whitespace-pre-wrap font-sans text-xs sm:text-sm text-slate-300">
                  {selectedDoc.content}
                </pre>
              </div>

              <div className="p-4 bg-slate-900/60 rounded-lg border border-slate-800 text-xs text-slate-400 flex items-center justify-between">
                <span>RAG Chunk Strategy: Semantic Section Preserving (Max 250 words/chunk)</span>
                <span className="font-mono text-indigo-300">Alembic Model: knowledge_documents</span>
              </div>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-slate-500 text-sm">
              Select a document to inspect full content
            </div>
          )}
        </div>
      </div>

      {/* Modal: Add Document */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white">Add Knowledge Base Article</h3>
            <div className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-300 mb-1">Title</label>
                <input
                  type="text"
                  value={newTitle}
                  onChange={e => setNewTitle(e.target.value)}
                  placeholder="e.g. Setting up BungeeCord & Velocity Proxy"
                  className="w-full bg-slate-950 border border-slate-800 rounded-md p-2 text-white"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">Category</label>
                <select
                  value={newCategory}
                  onChange={e => setNewCategory(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-md p-2 text-white"
                >
                  <option value="minecraft">Minecraft Hosting</option>
                  <option value="technical">Technical Support</option>
                  <option value="vps">VPS Support</option>
                  <option value="dedicated">Dedicated Servers</option>
                  <option value="billing">Billing Support</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">Tags (Comma-separated)</label>
                <input
                  type="text"
                  value={newTags}
                  onChange={e => setNewTags(e.target.value)}
                  placeholder="e.g. bungeecord, velocity, proxy, port"
                  className="w-full bg-slate-950 border border-slate-800 rounded-md p-2 text-white"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">Markdown Documentation Content</label>
                <textarea
                  rows={6}
                  value={newContent}
                  onChange={e => setNewContent(e.target.value)}
                  placeholder="Enter detailed technical steps, commands, and resolution..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-md p-2 text-white font-mono"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-slate-800">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleAddDoc}
                className="px-4 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-md cursor-pointer"
              >
                Index Document
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
