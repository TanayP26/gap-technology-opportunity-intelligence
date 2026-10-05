import type {
  AnalysisCreatePayload,
  AnalysisResponse,
  EvidenceListResponse,
  EvidenceType,
  LandscapeResponse,
} from "@/lib/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8050";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const message =
      body?.detail ??
      body?.error?.message ??
      `Request failed with ${response.status}`;
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function createAnalysis(payload: AnalysisCreatePayload) {
  return request<AnalysisResponse>("/api/v1/analyses", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getAnalysis(id: string) {
  return request<AnalysisResponse>(`/api/v1/analyses/${id}`);
}

export function getLandscape(id: string) {
  return request<LandscapeResponse>(`/api/v1/analyses/${id}/landscape`);
}

export function getEvidence(
  subdomainId: string,
  type?: EvidenceType,
  limit = 50,
  offset = 0,
) {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });
  if (type) params.set("evidence_type", type);

  return request<EvidenceListResponse>(
    `/api/v1/subdomains/${subdomainId}/evidence?${params.toString()}`,
  );
}

export { API_BASE };
