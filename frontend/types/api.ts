export type UserStoryPriority = 'low' | 'medium' | 'high'
export type UserStoryStatus = 'draft' | 'ready' | 'in-progress' | 'done'

export interface UserStory {
  id: number
  index: string
  title: string
  description: string
  constraints: string[]
  acceptanceCriteria: string[]
  priority: UserStoryPriority
  status: UserStoryStatus
  images: string[]
}

export interface TestCase {
  id: string
  titre: string
  catégorie: string
  préconditions: string
  étapes: string[]
  données_fictives: Record<string, unknown>
  résultat_attendu: string
  priorité: string
  user_story: string
  status: string
}

export interface AskResponse {
  status: string
  intent: string
  answer: string
  test_cases: TestCase[]
  ambiguities: string[]
  sources: string[]
  warnings: string[]
  requires_human_validation: boolean
}

export interface MetricsResponse {
  requests_total: number
  requests_success: number
  requests_error: number
  avg_response_time_ms: number
  test_cases_generated: number
}

export interface HealthResponse {
  status: string
  rag_indexed: boolean
  model: string
  version: string
}

export interface RagasResponse {
  selected_report: string
  report_file: string
  available_reports: string[]
  scores: Record<string, number | null>
  global_score: number | null
  n_samples: number | null
  model: string | null
}

export interface RagasRunRequest {
  report: string
  persist_report: boolean
  model?: string
  embedding_model?: string
  max_samples?: number
}

export interface RagasRunResponse {
  status: string
  report: string
  report_file: string | null
  persisted: boolean
  duration_ms: number
  available_reports: string[]
  scores: Record<string, number | null>
  global_score: number | null
  n_samples: number
  model: string
  embedding_model: string
}
