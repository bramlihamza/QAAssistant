import { createError, readBody } from 'h3'

interface GenerateBody {
  index?: string
  question?: string
  story?: {
    index?: string
    title?: string
    description?: string
    constraints?: string[]
    acceptanceCriteria?: string[]
    priority?: string
    status?: string
  }
}

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const body = await readBody<GenerateBody>(event)

  const normalizedIndex = body.index?.trim().toUpperCase() || body.story?.index?.trim().toUpperCase()

  const constraints = Array.isArray(body.story?.constraints)
    ? body.story.constraints.filter((value): value is string => typeof value === 'string' && value.trim().length > 0)
    : []
  const acceptanceCriteria = Array.isArray(body.story?.acceptanceCriteria)
    ? body.story.acceptanceCriteria.filter((value): value is string => typeof value === 'string' && value.trim().length > 0)
    : []

  const storyContext = body.story
    ? [
        `Index: ${normalizedIndex || 'US-???'}`,
        `Title: ${body.story.title?.trim() || 'N/A'}`,
        `Description: ${body.story.description?.trim() || 'N/A'}`,
        `Priority: ${body.story.priority?.trim() || 'N/A'}`,
        `Status: ${body.story.status?.trim() || 'N/A'}`,
        constraints.length > 0 ? `Constraints:\n- ${constraints.join('\n- ')}` : 'Constraints: N/A',
        acceptanceCriteria.length > 0
          ? `Acceptance Criteria:\n- ${acceptanceCriteria.join('\n- ')}`
          : 'Acceptance Criteria: N/A'
      ].join('\n')
    : ''

  const question = body.question?.trim() || [
    normalizedIndex ? `Generate test cases for ${normalizedIndex}.` : 'Generate test cases for this user story.',
    storyContext ? `Use this user story context:\n${storyContext}` : ''
  ]
    .filter(Boolean)
    .join('\n\n')

  if (!question) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Un index de user story ou une question explicite est requis.'
    })
  }

  try {
    return await $fetch(`${config.qaApiBase}/ask`, {
      method: 'POST',
      body: {
        question
      }
    })
  } catch (error) {
    throw createError({
      statusCode: 502,
      statusMessage: 'Erreur lors de la génération des tests via l\'API QA.',
      data: {
        error: String(error)
      }
    })
  }
})
