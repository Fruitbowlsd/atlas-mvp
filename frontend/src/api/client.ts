import type {
  AssessmentCreate,
  CurrentUser,
  EmailCheckResult,
  AssessmentDetail,
  AssessmentHistoryItem,
  AssessmentOut,
  AssessmentSummary,
  CalculateResult,
  ImportPreview,
  ProcessGroup,
  RegulatoryChange,
  RegulatoryChangeCreate,
  RegulatoryImpact,
  RegulatoryVersion,
  RegulatoryVersionCreate,
  RegulatoryVersionUpdate,
  SapCloudAlmForm,
  AdminAssessmentRow,
  AdminUser,
  AdminUserCreate,
  AssessmentDetail as AdminAssessmentDetail,
  SystemHealth,
  Tenant,
  TenantCreate,
  TenantUpdate,
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
  checkEmail: (email: string) =>
    request<EmailCheckResult>("/login/check-email", {
      method: "POST",
      body: JSON.stringify({ email }),
    }),

  login: (email: string, password: string) =>
    request<{ status: string; email: string }>("/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  logout: () => request<{ status: string; sso_logout_url: string | null }>("/logout", { method: "POST" }),

  me: () => request<CurrentUser>("/me"),
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

  listCustomerAssessments: (customerId: number) =>
    request<AssessmentHistoryItem[]>(`/customers/${customerId}/assessments`),

  createAssessmentForCustomer: (customerId: number, regulatoryVersionId: number) =>
    request<AssessmentOut>(`/customers/${customerId}/assessments`, {
      method: "POST",
      body: JSON.stringify({ regulatory_version_id: regulatoryVersionId }),
    }),

  listProcessGroups: () => request<ProcessGroup[]>("/process-groups"),

  listRegulatoryVersions: () => request<RegulatoryVersion[]>("/regulatory-versions"),

  createRegulatoryVersion: (payload: RegulatoryVersionCreate) =>
    request<RegulatoryVersion>("/regulatory-versions", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  updateRegulatoryVersion: (id: number, payload: RegulatoryVersionUpdate) =>
    request<RegulatoryVersion>(`/regulatory-versions/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  listRegulatoryChanges: (regulatoryVersionId: number) =>
    request<RegulatoryChange[]>(`/regulatory-changes?regulatory_version_id=${regulatoryVersionId}`),

  createRegulatoryChange: (payload: RegulatoryChangeCreate) =>
    request<RegulatoryChange>("/regulatory-changes", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  updateRegulatoryChange: (id: number, payload: Partial<RegulatoryChangeCreate & { status: string }>) =>
    request<RegulatoryChange>(`/regulatory-changes/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  deleteRegulatoryChange: (id: number) =>
    request<{ deleted: boolean }>(`/regulatory-changes/${id}`, { method: "DELETE" }),

  analyzeDiff: (versionId: number) =>
    request<RegulatoryChange[]>(`/regulatory-versions/${versionId}/analyze-diff`, { method: "POST" }),

  getRegulatoryImpact: (assessmentId: number) =>
    request<RegulatoryImpact>(`/assessments/${assessmentId}/regulatory-impact`),

  // --- Admin (Issue #13) ---
  adminListTenants: () => request<Tenant[]>("/admin/tenants"),

  adminCreateTenant: (payload: TenantCreate) =>
    request<Tenant>("/admin/tenants", { method: "POST", body: JSON.stringify(payload) }),

  adminUpdateTenant: (id: number, payload: TenantUpdate) =>
    request<Tenant>(`/admin/tenants/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),

  adminListUsers: () => request<AdminUser[]>("/admin/users"),

  adminCreateUser: (payload: AdminUserCreate) =>
    request<AdminUser>("/admin/users", { method: "POST", body: JSON.stringify(payload) }),

  adminUpdateUser: (id: number, payload: { is_active?: boolean; is_atlas_admin?: boolean }) =>
    request<AdminUser>(`/admin/users/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),

  adminListAssessments: (tenantId?: number) =>
    request<AdminAssessmentRow[]>(`/admin/assessments${tenantId ? `?tenant_id=${tenantId}` : ""}`),

  adminGetAssessment: (id: number) => request<AdminAssessmentDetail>(`/admin/assessments/${id}`),

  adminSystemHealth: () => request<SystemHealth>("/admin/system/health"),

  adminReseed: () => request<{ status: string }>("/admin/system/reseed", { method: "POST" }),
};
