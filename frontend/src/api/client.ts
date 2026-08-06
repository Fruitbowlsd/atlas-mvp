import type {
  AssessmentCreate,
  AssessmentDetail,
  AssessmentOut,
  AssessmentSummary,
  CalculateResult,
  ImportPreview,
  SapCloudAlmForm,
} from "../types";

const BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API-Fehler ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  login: (password: string) =>
    request<{ status: string }>("/login", {
      method: "POST",
      body: JSON.stringify({ password }),
    }),

  checkAuth: () => request<{ authenticated: boolean }>("/login/check"),
  listAssessments: () => request<AssessmentSummary[]>("/assessments"),

  createAssessment: (payload: AssessmentCreate) =>
    request<AssessmentOut>("/assessments", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  getAssessment: (id: number) => request<AssessmentDetail>(`/assessments/${id}`),

  updateRequirementStatus: (
    assessmentRequirementId: number,
    payload: Partial<{
      implementation_status: string;
      test_status: string;
      result_status: string;
      evidence_status: string;
      comment: string;
      responsible_person: string;
    }>
  ) =>
    request(`/assessments/requirement-status/${assessmentRequirementId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),

  calculate: (id: number) =>
    request<CalculateResult>(`/assessments/${id}/calculate`, { method: "POST" }),

  importCsvPreview: async (assessmentId: number, file: File) => {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${BASE}/assessments/${assessmentId}/import/csv`, {
      method: "POST",
      credentials: "include",
      body: form,
    });
    if (!res.ok) throw new Error(`API-Fehler ${res.status}: ${await res.text()}`);
    return res.json() as Promise<ImportPreview>;
  },

  importSapCloudAlmPreview: (assessmentId: number, payload: SapCloudAlmForm) =>
    request<ImportPreview>(`/assessments/${assessmentId}/import/sap-cloud-alm`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  importConfirm: (
    assessmentId: number,
    sourceName: string,
    items: { requirement_id: number; implementation_status: string; test_status: string; result_status: string }[]
  ) =>
    request<{ updated: number }>(`/assessments/${assessmentId}/import/confirm`, {
      method: "POST",
      body: JSON.stringify({ source_name: sourceName, items }),
    }),
};
