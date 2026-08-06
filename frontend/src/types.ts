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
