import {
  BookOpen,
  Bot,
  CheckCircle2,
  Database,
  Edit3,
  FileText,
  Loader2,
  MessageSquare,
  Plus,
  RefreshCw,
  Save,
  Search,
  Send,
  Settings,
  Trash2,
  Upload,
  X,
} from "lucide-react";
import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { AnswerMeApi, getStoredApiBase, setStoredApiBase } from "./api";
import type { ChatAnswer, DocumentItem, HealthStatus, KnowledgeBase, Message, ViewKey } from "./types";

const views: Array<{ key: ViewKey; label: string; icon: typeof MessageSquare }> = [
  { key: "chat", label: "问答", icon: MessageSquare },
  { key: "knowledge", label: "知识库", icon: Database },
  { key: "documents", label: "文档", icon: FileText },
  { key: "settings", label: "设置", icon: Settings },
];

function formatDate(value: string | number) {
  const date = typeof value === "number" ? new Date(value * 1000) : new Date(value);
  return Number.isNaN(date.getTime()) ? "-" : date.toLocaleString();
}

function formatSize(value?: number | null) {
  if (!value) return "-";
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / 1024 / 1024).toFixed(1)} MB`;
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    completed: "已完成",
    processing: "处理中",
    pending: "待处理",
    failed: "失败",
  };
  return map[status] || status;
}

type UploadProgress = {
  filename: string;
  percent: number;
  status: "uploading" | "processing";
};

export function App() {
  const [apiBase, setApiBase] = useState(getStoredApiBase);
  const api = useMemo(() => new AnswerMeApi(apiBase), [apiBase]);
  const [activeView, setActiveView] = useState<ViewKey>("chat");
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [selectedKbId, setSelectedKbId] = useState("");
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [lastAnswer, setLastAnswer] = useState<ChatAnswer | null>(null);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<Record<string, UploadProgress>>({});

  const selectedKb = knowledgeBases.find((kb) => kb.id === selectedKbId);

  const reportError = useCallback((err: unknown) => {
    setError(err instanceof Error ? err.message : "操作失败");
  }, []);

  const refreshAll = useCallback(async () => {
    setError("");
    try {
      const [healthResult, kbResult, docsResult] = await Promise.all([
        api.health().catch(() => null),
        api.listKnowledgeBases(),
        api.listDocuments(),
      ]);
      setHealth(healthResult);
      setKnowledgeBases(kbResult);
      setDocuments(docsResult.documents);
      if (!selectedKbId && kbResult.length > 0) setSelectedKbId(kbResult[0].id);
    } catch (err) {
      reportError(err);
    }
  }, [api, reportError, selectedKbId]);

  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  useEffect(() => {
    if (!notice) return;
    const timer = window.setTimeout(() => setNotice(""), 3000);
    return () => window.clearTimeout(timer);
  }, [notice]);

  useEffect(() => {
    if (!selectedKbId) {
      setMessages([]);
      return;
    }
    api
      .getHistory(selectedKbId)
      .then((history) => setMessages(history.messages))
      .catch(() => setMessages([]));
  }, [api, selectedKbId]);

  function saveApiBase(value: string) {
    setStoredApiBase(value);
    setApiBase(value.replace(/\/$/, ""));
    setNotice("API 地址已保存");
  }

  async function sendQuestion(question: string, temperature: number, topK: number) {
    if (!selectedKbId) {
      setError("请先创建或选择知识库");
      return;
    }
    const nextMessages: Message[] = [...messages, { role: "user", content: question }];
    setMessages(nextMessages);
    setLoading(true);
    setError("");
    try {
      const answer = await api.ask({
        question,
        knowledge_base_id: selectedKbId,
        history: messages,
        temperature,
        top_k: topK,
      });
      setLastAnswer(answer);
      setMessages([...nextMessages, { role: "assistant", content: answer.answer }]);
    } catch (err) {
      setMessages(messages);
      reportError(err);
    } finally {
      setLoading(false);
    }
  }

  async function clearChat() {
    if (!selectedKbId) return;
    await api.clearHistory(selectedKbId);
    setMessages([]);
    setLastAnswer(null);
  }

  async function createKnowledgeBase(payload: { name: string; description: string }) {
    setLoading(true);
    setError("");
    try {
      const kb = await api.createKnowledgeBase(payload);
      setKnowledgeBases((items) => [kb, ...items]);
      setSelectedKbId(kb.id);
      setNotice("知识库已创建");
    } catch (err) {
      reportError(err);
    } finally {
      setLoading(false);
    }
  }

  async function updateKnowledgeBase(id: string, payload: { name: string; description: string }) {
    setLoading(true);
    setError("");
    try {
      const kb = await api.updateKnowledgeBase(id, payload);
      setKnowledgeBases((items) => items.map((item) => (item.id === id ? kb : item)));
      setNotice("知识库已更新");
      return true;
    } catch (err) {
      reportError(err);
      return false;
    } finally {
      setLoading(false);
    }
  }

  async function uploadDocument(kbId: string, file: File) {
    setLoading(true);
    setError("");
    setUploadProgress((items) => ({
      ...items,
      [kbId]: { filename: file.name, percent: 0, status: "uploading" },
    }));
    try {
      await api.uploadDocumentWithProgress(kbId, file, (percent) => {
        setUploadProgress((items) => ({
          ...items,
          [kbId]: { filename: file.name, percent, status: percent >= 100 ? "processing" : "uploading" },
        }));
      });
      setNotice("文档上传完成");
      await refreshAll();
    } catch (err) {
      reportError(err);
    } finally {
      setLoading(false);
      setUploadProgress((items) => {
        const next = { ...items };
        delete next[kbId];
        return next;
      });
    }
  }

  async function deleteDocument(document: DocumentItem) {
    if (!confirm(`删除文档「${document.filename}」？`)) return;
    await api.deleteDocument(document);
    setDocuments((items) => items.filter((item) => item.id !== document.id));
  }

  async function deleteKnowledgeBase(id: string) {
    if (!confirm("删除该知识库及其文档？")) return;
    await api.deleteKnowledgeBase(id);
    setKnowledgeBases((items) => items.filter((item) => item.id !== id));
    setDocuments((items) => items.filter((item) => item.knowledge_base_id !== id));
    if (selectedKbId === id) setSelectedKbId("");
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Bot size={28} />
          <div>
            <strong>AnswerMe</strong>
            <span>RAG 问答系统</span>
          </div>
        </div>
        <nav>
          {views.map((view) => {
            const Icon = view.icon;
            return (
              <button
                key={view.key}
                className={activeView === view.key ? "nav-item active" : "nav-item"}
                onClick={() => setActiveView(view.key)}
                title={view.label}
              >
                <Icon size={18} />
                <span>{view.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <h1>{views.find((view) => view.key === activeView)?.label}</h1>
            <p>{selectedKb ? `当前知识库：${selectedKb.name}` : "连接后端并选择知识库开始使用"}</p>
          </div>
          <div className="topbar-actions">
            <span className={health?.status === "healthy" ? "health ok" : "health"}>
              <CheckCircle2 size={16} />
              {health?.status || "未连接"}
            </span>
            <select value={selectedKbId} onChange={(event) => setSelectedKbId(event.target.value)}>
              <option value="">选择知识库</option>
              {knowledgeBases.map((kb) => (
                <option key={kb.id} value={kb.id}>
                  {kb.name}
                </option>
              ))}
            </select>
            <button className="icon-button" onClick={refreshAll} title="刷新">
              <RefreshCw size={18} />
            </button>
          </div>
        </header>

        {(error || notice) && <div className={error ? "alert error" : "alert"}>{error || notice}</div>}

        {activeView === "chat" && (
          <ChatView
            loading={loading}
            messages={messages}
            answer={lastAnswer}
            disabled={!selectedKbId}
            onSend={sendQuestion}
            onClear={clearChat}
          />
        )}
        {activeView === "knowledge" && (
          <KnowledgeView
            loading={loading}
            knowledgeBases={knowledgeBases}
            documents={documents}
            uploadProgress={uploadProgress}
            selectedKbId={selectedKbId}
            onSelect={setSelectedKbId}
            onCreate={createKnowledgeBase}
            onUpdate={updateKnowledgeBase}
            onDelete={deleteKnowledgeBase}
            onUpload={uploadDocument}
          />
        )}
        {activeView === "documents" && (
          <DocumentsView
            documents={documents}
            knowledgeBases={knowledgeBases}
            selectedKbId={selectedKbId}
            onFilter={setSelectedKbId}
            onDelete={deleteDocument}
          />
        )}
        {activeView === "settings" && (
          <SettingsView apiBase={apiBase} health={health} onSave={saveApiBase} />
        )}
      </main>
    </div>
  );
}

function ChatView(props: {
  loading: boolean;
  messages: Message[];
  answer: ChatAnswer | null;
  disabled: boolean;
  onSend: (question: string, temperature: number, topK: number) => void;
  onClear: () => void;
}) {
  const [question, setQuestion] = useState("");
  const [temperature, setTemperature] = useState(0.7);
  const [topK, setTopK] = useState(5);

  function submit(event: FormEvent) {
    event.preventDefault();
    if (!question.trim() || props.loading) return;
    props.onSend(question.trim(), temperature, topK);
    setQuestion("");
  }

  return (
    <section className="workspace chat-layout">
      <div className="chat-panel">
        <div className="message-list">
          {props.messages.length === 0 && (
            <div className="empty-state">
              <MessageSquare size={36} />
              <strong>开始一次知识库问答</strong>
              <span>选择知识库后输入问题，答案会附带检索来源。</span>
            </div>
          )}
          {props.messages.map((message, index) => (
            <article key={`${message.role}-${index}`} className={`message ${message.role}`}>
              <span>{message.role === "user" ? "你" : "AnswerMe"}</span>
              <p>{message.content}</p>
            </article>
          ))}
          {props.loading && (
            <article className="message assistant">
              <span>AnswerMe</span>
              <p className="typing">
                <Loader2 size={16} /> 正在检索并生成回答...
              </p>
            </article>
          )}
        </div>
        <form className="composer" onSubmit={submit}>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder={props.disabled ? "请先选择知识库" : "输入你的问题..."}
            disabled={props.disabled}
          />
          <div className="composer-actions">
            <label>
              温度
              <input
                type="number"
                min="0"
                max="2"
                step="0.1"
                value={temperature}
                onChange={(event) => setTemperature(Number(event.target.value))}
              />
            </label>
            <label>
              Top K
              <input
                type="number"
                min="1"
                max="20"
                value={topK}
                onChange={(event) => setTopK(Number(event.target.value))}
              />
            </label>
            <button type="button" className="secondary" onClick={props.onClear}>
              清空
            </button>
            <button type="submit" disabled={props.disabled || props.loading || !question.trim()}>
              <Send size={16} /> 发送
            </button>
          </div>
        </form>
      </div>
      <aside className="side-panel">
        <h2>来源文档</h2>
        {!props.answer?.sources?.length && <p className="muted">回答后显示相似文档片段。</p>}
        {props.answer?.sources?.map((source, index) => (
          <div className="source-card" key={`${source.document_id}-${index}`}>
            <strong>{source.document_id}</strong>
            <span>相似度 {source.score.toFixed(3)}</span>
            <p>{source.content}</p>
          </div>
        ))}
      </aside>
    </section>
  );
}

function KnowledgeView(props: {
  loading: boolean;
  knowledgeBases: KnowledgeBase[];
  documents: DocumentItem[];
  uploadProgress: Record<string, UploadProgress>;
  selectedKbId: string;
  onSelect: (id: string) => void;
  onCreate: (payload: { name: string; description: string }) => void;
  onUpdate: (id: string, payload: { name: string; description: string }) => Promise<boolean>;
  onDelete: (id: string) => void;
  onUpload: (kbId: string, file: File) => void;
}) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [editingId, setEditingId] = useState("");
  const [editName, setEditName] = useState("");
  const [editDescription, setEditDescription] = useState("");

  function submit(event: FormEvent) {
    event.preventDefault();
    if (!name.trim()) return;
    props.onCreate({ name: name.trim(), description: description.trim() });
    setName("");
    setDescription("");
  }

  function startEdit(kb: KnowledgeBase) {
    setEditingId(kb.id);
    setEditName(kb.name);
    setEditDescription(kb.description || "");
  }

  function cancelEdit() {
    setEditingId("");
    setEditName("");
    setEditDescription("");
  }

  async function submitUpdate(event: FormEvent, kbId: string) {
    event.preventDefault();
    if (!editName.trim()) return;
    const saved = await props.onUpdate(kbId, {
      name: editName.trim(),
      description: editDescription.trim(),
    });
    if (saved) cancelEdit();
  }

  return (
    <section className="workspace split-layout">
      <form className="panel form-panel" onSubmit={submit}>
        <h2>创建知识库</h2>
        <label>
          名称
          <input value={name} onChange={(event) => setName(event.target.value)} placeholder="例如：产品手册" />
        </label>
        <label>
          描述
          <textarea
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            placeholder="知识库用途、文档范围或维护说明"
          />
        </label>
        <button type="submit" disabled={props.loading || !name.trim()}>
          <Plus size={16} /> 创建
        </button>
      </form>

      <div className="panel">
        <h2>知识库列表</h2>
        <div className="kb-grid">
          {props.knowledgeBases.map((kb) => {
            const kbDocs = props.documents.filter((document) => document.knowledge_base_id === kb.id);
            const isEditing = editingId === kb.id;
            const progress = props.uploadProgress[kb.id];
            return (
              <article key={kb.id} className={props.selectedKbId === kb.id ? "kb-card selected" : "kb-card"}>
                {isEditing ? (
                  <form className="kb-edit-form" onSubmit={(event) => submitUpdate(event, kb.id)}>
                    <label>
                      名称
                      <input value={editName} onChange={(event) => setEditName(event.target.value)} />
                    </label>
                    <label>
                      描述
                      <textarea value={editDescription} onChange={(event) => setEditDescription(event.target.value)} />
                    </label>
                    <div className="card-meta">
                      <span>{kb.document_count || kbDocs.length} 个文档</span>
                      <span>{formatDate(kb.updated_at)}</span>
                    </div>
                    <div className="card-actions">
                      <button type="submit" disabled={props.loading || !editName.trim()}>
                        <Save size={16} /> 保存
                      </button>
                      <button type="button" className="secondary" onClick={cancelEdit} disabled={props.loading}>
                        <X size={16} /> 取消
                      </button>
                    </div>
                  </form>
                ) : (
                  <>
                    <button type="button" className="card-main" onClick={() => props.onSelect(kb.id)}>
                      <BookOpen size={20} />
                      <strong>{kb.name}</strong>
                      <span>{kb.description || "无描述"}</span>
                    </button>
                    <div className="card-meta">
                      <span>{kb.document_count || kbDocs.length} 个文档</span>
                      <span>{formatDate(kb.updated_at)}</span>
                    </div>
                    <div className="card-actions">
                      <label className="upload-button">
                        <Upload size={16} /> {progress ? "上传中" : "上传"}
                        <input
                          type="file"
                          accept=".pdf,.docx,.txt,.md"
                          disabled={Boolean(progress)}
                          onChange={(event) => {
                            const file = event.target.files?.[0];
                            if (file) props.onUpload(kb.id, file);
                            event.currentTarget.value = "";
                          }}
                        />
                      </label>
                      <button type="button" className="secondary" onClick={() => startEdit(kb)}>
                        <Edit3 size={16} /> 编辑
                      </button>
                      <button type="button" className="danger" onClick={() => props.onDelete(kb.id)}>
                        <Trash2 size={16} /> 删除
                      </button>
                    </div>
                    {progress && (
                      <div className="upload-progress" role="status" aria-live="polite">
                        <div className="upload-progress-meta">
                          <span>{progress.filename}</span>
                          <strong>{progress.status === "processing" ? "处理中" : `${progress.percent}%`}</strong>
                        </div>
                        <div className="upload-progress-track">
                          <div className="upload-progress-bar" style={{ width: `${progress.percent}%` }} />
                        </div>
                      </div>
                    )}
                  </>
                )}
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function DocumentsView(props: {
  documents: DocumentItem[];
  knowledgeBases: KnowledgeBase[];
  selectedKbId: string;
  onFilter: (id: string) => void;
  onDelete: (document: DocumentItem) => void;
}) {
  const [query, setQuery] = useState("");
  const filtered = props.documents.filter((document) => {
    const matchesKb = !props.selectedKbId || document.knowledge_base_id === props.selectedKbId;
    const matchesQuery = document.filename.toLowerCase().includes(query.toLowerCase());
    return matchesKb && matchesQuery;
  });

  return (
    <section className="workspace panel">
      <div className="table-toolbar">
        <div className="search-box">
          <Search size={17} />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索文档名" />
        </div>
        <select value={props.selectedKbId} onChange={(event) => props.onFilter(event.target.value)}>
          <option value="">全部知识库</option>
          {props.knowledgeBases.map((kb) => (
            <option key={kb.id} value={kb.id}>
              {kb.name}
            </option>
          ))}
        </select>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>文件</th>
              <th>状态</th>
              <th>大小</th>
              <th>分块</th>
              <th>更新时间</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((document) => (
              <tr key={document.id}>
                <td>
                  <strong>{document.filename}</strong>
                  <span>{document.content_preview || document.id}</span>
                </td>
                <td>
                  <span className={`status ${document.status}`}>{statusLabel(document.status)}</span>
                </td>
                <td>{formatSize(document.file_size)}</td>
                <td>{document.chunk_count ?? "-"}</td>
                <td>{formatDate(document.updated_at)}</td>
                <td>
                  <button className="icon-button danger" onClick={() => props.onDelete(document)} title="删除文档">
                    <Trash2 size={17} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && <div className="empty-row">暂无文档</div>}
      </div>
    </section>
  );
}

function SettingsView(props: {
  apiBase: string;
  health: HealthStatus | null;
  onSave: (value: string) => void;
}) {
  const [value, setValue] = useState(props.apiBase);

  return (
    <section className="workspace split-layout">
      <form
        className="panel form-panel"
        onSubmit={(event) => {
          event.preventDefault();
          props.onSave(value);
        }}
      >
        <h2>后端连接</h2>
        <label>
          API Base URL
          <input value={value} onChange={(event) => setValue(event.target.value)} placeholder="http://localhost:8000" />
        </label>
        <button type="submit">
          <Settings size={16} /> 保存
        </button>
      </form>
      <div className="panel">
        <h2>服务状态</h2>
        <dl className="details">
          <dt>状态</dt>
          <dd>{props.health?.status || "未连接"}</dd>
          <dt>版本</dt>
          <dd>{props.health?.version || "-"}</dd>
          <dt>检查时间</dt>
          <dd>{props.health ? formatDate(props.health.timestamp) : "-"}</dd>
          <dt>Swagger</dt>
          <dd>
            <a href={`${props.apiBase}/docs`} target="_blank" rel="noreferrer">
              {props.apiBase}/docs
            </a>
          </dd>
        </dl>
      </div>
    </section>
  );
}
