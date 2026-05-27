import { createError, readBody } from 'h3'

interface RagasRunBody {
  report?: string
  persist_report?: boolean
  model?: string
  embedding_model?: string
  max_samples?: number
}

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const body = await readBody<RagasRunBody>(event)

  const payload = {
    report: body.report || 'reranker',
    persist_report: body.persist_report ?? true,
    model: body.model,
    embedding_model: body.embedding_model,
    max_samples: body.max_samples
  }

  try {
    return await $fetch(`${config.qaApiBase}/ragas/run`, {
      method: 'POST',
      body: payload
    })
  } catch (error) {
    const raw = error as {
      status?: number
      statusCode?: number
      statusMessage?: string
      message?: string
      data?: { detail?: string; error?: string }
      response?: { status?: number; _data?: { detail?: string; error?: string } }
    }

    const backendStatus =
      raw.statusCode ||
      raw.status ||
      raw.response?.status ||
      502

    const backendDetail =
      raw.data?.detail ||
      raw.response?._data?.detail ||
      raw.data?.error ||
      raw.response?._data?.error ||
      raw.statusMessage ||
      raw.message ||
      'Erreur inconnue'

    const endpointHint = backendStatus === 404
      ? "Endpoint '/ragas/run' introuvable sur l'API QA. Redémarre le backend avec la dernière version."
      : String(backendDetail)

    throw createError({
      statusCode: backendStatus,
      statusMessage: endpointHint,
      data: {
        backendStatus,
        backendDetail
      }
    })
  }
})
