import type {
  ChatAnswer,
  ChatHistory,
  DocumentItem,
  DocumentList,
  Envelope,
  HealthStatus,
  KnowledgeBase,
  KnowledgeBasePayload,
  Message,
  UploadResult,
} from "./types";

const DEFAULT_API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export function getStoredApiBase() {
  return localStorage.getItem("answerme.apiBase") || DEFAULT_API_BASE;
}

export function setStoredApiBase(value: string) {
  localStorage.setItem("answerme.apiBase", value.replace(/\/$/, ""));
}

async function parseResponse<T>(response: Response): Promise<T> {
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail = typeof payload === "object" && payload !== null ? payload.detail : payload;
    throw new Error(typeof detail === "string" ? detail : response.statusText);
  }

  return payload as T;
}

export class AnswerMeApi {
  constructor(private baseUrl: string) {}

  setBaseUrl(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  private url(path: string) {
    return `${this.baseUrl}${path}`;
  }

  async health() {
    return parseResponse<HealthStatus>(await fetch(this.url("/api/v1/health/")));
  }

  async listKnowledgeBases() {
    return parseResponse<KnowledgeBase[]>(await fetch(this.url("/api/v1/knowledge-base/")));
  }

  async createKnowledgeBase(payload: KnowledgeBasePayload) {
    return parseResponse<KnowledgeBase>(
      await fetch(this.url("/api/v1/knowledge-base/"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }),
    );
  }

  async updateKnowledgeBase(id: string, payload: Partial<KnowledgeBasePayload>) {
    return parseResponse<KnowledgeBase>(
      await fetch(this.url(`/api/v1/knowledge-base/${id}`), {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }),
    );
  }

  async deleteKnowledgeBase(id: string) {
    return parseResponse<{ success: boolean; message: string }>(
      await fetch(this.url(`/api/v1/knowledge-base/${id}`), { method: "DELETE" }),
    );
  }

  async uploadDocument(kbId: string, file: File) {
    return this.uploadDocumentWithProgress(kbId, file);
  }

  uploadDocumentWithProgress(kbId: string, file: File, onProgress?: (progress: number) => void) {
    const formData = new FormData();
    formData.append("file", file);

    return new Promise<UploadResult>((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open("POST", this.url(`/api/v1/knowledge-base/${kbId}/upload`));

      xhr.upload.onprogress = (event) => {
        if (!event.lengthComputable) return;
        onProgress?.(Math.round((event.loaded / event.total) * 100));
      };

      xhr.onload = () => {
        const contentType = xhr.getResponseHeader("content-type") || "";
        const payload = contentType.includes("application/json") ? JSON.parse(xhr.responseText) : xhr.responseText;

        if (xhr.status < 200 || xhr.status >= 300) {
          const detail = typeof payload === "object" && payload !== null ? payload.detail : payload;
          reject(new Error(typeof detail === "string" ? detail : xhr.statusText || "上传失败"));
          return;
        }

        resolve(payload as UploadResult);
      };

      xhr.onerror = () => reject(new Error("上传失败，请检查后端连接"));
      xhr.onabort = () => reject(new Error("上传已取消"));
      xhr.send(formData);
    });
  }

  async listDocuments(knowledgeBaseId?: string) {
    const params = new URLSearchParams({ page: "1", page_size: "100" });
    if (knowledgeBaseId) params.set("knowledge_base_id", knowledgeBaseId);
    return parseResponse<DocumentList>(await fetch(this.url(`/api/v1/documents/?${params}`)));
  }

  async deleteDocument(document: DocumentItem) {
    return parseResponse<{ success: boolean; document_id: string }>(
      await fetch(this.url(`/api/v1/documents/${document.knowledge_base_id}/${document.id}`), {
        method: "DELETE",
      }),
    );
  }

  async getHistory(knowledgeBaseId: string) {
    const params = new URLSearchParams({ knowledge_base_id: knowledgeBaseId, limit: "60" });
    const response = await parseResponse<Envelope<ChatHistory>>(
      await fetch(this.url(`/api/v1/chat/history?${params}`)),
    );
    if (!response.success || !response.data) throw new Error(response.error?.message || "加载历史失败");
    return response.data;
  }

  async clearHistory(knowledgeBaseId: string) {
    const params = new URLSearchParams({ knowledge_base_id: knowledgeBaseId });
    return parseResponse<Envelope<{ cleared: boolean }>>(
      await fetch(this.url(`/api/v1/chat/history?${params}`), { method: "DELETE" }),
    );
  }

  async ask(input: {
    question: string;
    knowledge_base_id: string;
    history: Message[];
    temperature?: number;
    top_k?: number;
  }) {
    const response = await parseResponse<Envelope<ChatAnswer>>(
      await fetch(this.url("/api/v1/chat/query"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input),
      }),
    );
    if (!response.success || !response.data) throw new Error(response.error?.message || "问答请求失败");
    return response.data;
  }
}
