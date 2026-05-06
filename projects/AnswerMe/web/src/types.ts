export type ViewKey = "chat" | "knowledge" | "documents" | "settings";

export interface Message {
  role: "user" | "assistant";
  content: string;
}

export interface SourceDocument {
  document_id: string;
  content: string;
  score: number;
  metadata?: Record<string, unknown> | null;
}

export interface ChatAnswer {
  answer: string;
  sources: SourceDocument[];
  response_time_ms: number;
  knowledge_base_id: string;
  question: string;
}

export interface Envelope<T> {
  success: boolean;
  data?: T;
  error?: {
    code?: number;
    message?: string;
    details?: string;
  } | null;
}

export interface KnowledgeBase {
  id: string;
  name: string;
  description: string;
  document_count: number;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeBasePayload {
  name: string;
  description?: string;
}

export interface DocumentItem {
  id: string;
  filename: string;
  knowledge_base_id: string;
  status: "pending" | "processing" | "completed" | "failed" | string;
  page_count?: number | null;
  chunk_count?: number | null;
  file_size?: number | null;
  content_preview?: string | null;
  created_at: string | number;
  updated_at: string | number;
}

export interface DocumentList {
  documents: DocumentItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface UploadResult {
  document_id: string;
  filename: string;
  pages: number;
  chunk_count: number;
  status: string;
}

export interface ChatHistory {
  messages: Message[];
  total: number;
  knowledge_base_id: string;
}

export interface HealthStatus {
  status: string;
  version: string;
  timestamp: string;
}
