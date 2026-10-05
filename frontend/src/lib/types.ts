export type ScoreStatus = "scored" | "insufficient_evidence";
export type AnalysisStatus = "draft" | "planned" | "running" | "complete" | "failed";
export type EvidenceType = "paper" | "patent" | "news" | "market";

export type SignalVector = {
  research: number | null;
  patents: number | null;
  attention: number | null;
  events: number | null;
  market: number | null;
  confidence: number;
};

export type Score = {
  signals: SignalVector;
  status: ScoreStatus;
  missing_signals: string[];
  technical_momentum: number | null;
  demand_momentum: number | null;
  whitespace: number | null;
  gap_score: number | null;
};

export type SubdomainAnalysis = {
  id: string;
  name: string;
  position: number;
  signals: SignalVector;
  score: Score;
  evidence_count: number;
  source_error_count: number;
};

export type AnalysisResponse = {
  id: string;
  technology: string;
  geography: string;
  status: AnalysisStatus;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  failure_reason: string | null;
  subdomains: SubdomainAnalysis[];
};

export type LandscapeEntry = {
  subdomain_id: string;
  name: string;
  position: number;
  signals: SignalVector;
  score_status: ScoreStatus;
  missing_signals: string[];
  technical_momentum: number | null;
  demand_momentum: number | null;
  whitespace: number | null;
  gap_score: number | null;
  evidence_count: number;
  source_error_count: number;
};

export type LandscapeResponse = {
  analysis_id: string;
  technology: string;
  status: AnalysisStatus;
  entries: LandscapeEntry[];
};

export type EvidenceItem = {
  id: string;
  evidence_type: EvidenceType;
  title: string;
  url: string | null;
  source_name: string | null;
  published_at: string | null;
  snippet: string | null;
  external_id: string | null;
  metadata: Record<string, unknown>;
};

export type EvidenceListResponse = {
  subdomain_id: string;
  total: number;
  limit: number;
  offset: number;
  items: EvidenceItem[];
};

export type AnalysisCreatePayload = {
  technology: string;
  subdomains: string[];
  geography: string;
  confirm_live_search: true;
};
