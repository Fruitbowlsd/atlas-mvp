export interface ProcessIdentifier {
  id: number;
  pi_number: string;
  name: string;
  sender_role: string | null;
  receiver_role: string | null;
  message_type: string;
  criticality: string;
}

export interface ProcessGroup {
  id: number;
  code: string;
  name: string;
  sequence: number;
  pis: ProcessIdentifier[];
}

export interface Requirement {
  id: number;
  code: string;
  title: string;
  description: string | null;
  pi_id: number | null;
  transaction_reason: string | null;
  response_code: string | null;
  criticality: string;
  weight: number;
  applies_to_slp: boolean;
  applies_to_rlm: boolean;
}

export interface AssessmentRequirement {
  id: number;
  requirement_id: number;
  relevance_status: string;
  implementation_status: string;
  test_status: string;
  result_status: string;
  evidence_status: string;
  comment: string | null;
  responsible_person: string | null;
  requirement: Requirement;
}

export interface ScoreResult {
  regulatory_coverage: number;
  quality_grade: number;
  implementation_quality: number;
  test_quality: number;
  evidence_quality: number;
  actuality: number;
}

export interface Finding {
  id: number;
  severity: string;
  title: string;
  description: string | null;
  recommendation: string | null;
}

export interface HeatmapRow {
  process_group: string;
  coverage: number;
  quality: number;
  status: "gruen" | "gelb" | "rot";
}

export interface AssessmentSummary {
  id: number;
  customer_name: string | null;
  business_scenario: string;
  customer_segments: string;
  status: string;
}

export type MarketRole = "lieferant" | "grund_ersatzversorger" | "beides";

export interface AssessmentOut {
  id: number;
  customer_id: number;
  customer_name: string | null;
  market_role: MarketRole | null;
  business_scenario: string;
  customer_segments: string;
  status: string;
  created_at: string;
}

export interface AssessmentCreate {
  customer_name: string;
  market_role: MarketRole;
  customer_segments: string;
  business_scenario?: string;
}

export interface AssessmentDetail {
  assessment: AssessmentOut;
  requirement_statuses: AssessmentRequirement[];
  score: ScoreResult | null;
  findings: Finding[];
  process_groups: ProcessGroup[];
}

export interface ImportSuggestion {
  row_index: number;
  raw_title: string;
  raw_status: string;
  requirement_id: number | null;
  requirement_code: string | null;
  requirement_title: string | null;
  confidence: number;
  implementation_status: string;
  test_status: string;
  result_status: string;
}

export interface ImportPreview {
  source_name: string;
  suggestions: ImportSuggestion[];
}

export interface SapCloudAlmForm {
  token_url: string;
  client_id: string;
  client_secret: string;
  base_url: string;
  api_path: string;
}

export interface CalculateResult {
  score: ScoreResult;
  findings: Finding[];
  heatmap: HeatmapRow[];
}

export interface RegulatoryVersion {
  id: number;
  name: string;
  sector: string;
  status: string;
  source_reference: string | null;
  is_active: boolean;
  valid_from: string | null;
  predecessor_version_id: number | null;
}

export interface RegulatoryVersionCreate {
  name: string;
  sector?: string;
  status?: string;
  source_reference?: string | null;
  valid_from?: string | null;
  predecessor_version_id?: number | null;
}

export type ChangeCategory =
  | "neuer_prozess"
  | "neues_pflichtfeld"
  | "neuer_code"
  | "neue_qualitaetsregel"
  | "neuer_testfall";

export type RiskLevel = "hoch" | "mittel" | "niedrig";
export type ChangeStatus = "zu_pruefen" | "entwurf" | "veroeffentlicht";

export interface RegulatoryChange {
  id: number;
  title: string;
  description: string | null;
  category: ChangeCategory;
  process_group_id: number | null;
  process_group_name: string | null;
  pi_id: number | null;
  pi_number: string | null;
  risk: RiskLevel;
  effort: RiskLevel;
  source_url: string | null;
  status: ChangeStatus;
  origin: "manuell" | "ki_vorschlag";
  regulatory_version_id: number;
  created_at: string;
}

export interface RegulatoryImpactRequirementRef {
  requirement_code: string;
  title: string;
  pi_number: string | null;
}

export interface RegulatoryImpact {
  has_upcoming_version: boolean;
  upcoming_version_id: number | null;
  upcoming_version_name: string | null;
  upcoming_version_valid_from: string | null;
  current_coverage: number | null;
  projected_coverage: number | null;
  remain_valid_count: number;
  newly_required: RegulatoryImpactRequirementRef[];
  dropped: RegulatoryImpactRequirementRef[];
  published_change_count: number;
  risk_hoch_count: number;
  risk_mittel_count: number;
  risk_niedrig_count: number;
  affected_process_groups: string[];
  new_test_case_count: number;
}

export interface RegulatoryChangeCreate {
  title: string;
  description?: string | null;
  category: ChangeCategory;
  process_group_id?: number | null;
  pi_id?: number | null;
  risk?: RiskLevel;
  effort?: RiskLevel;
  source_url?: string | null;
  regulatory_version_id: number;
}
