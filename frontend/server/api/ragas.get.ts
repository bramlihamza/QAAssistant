import { createError, getQuery } from 'h3'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const query = getQuery(event)
  const report = typeof query.report === 'string' ? query.report : undefined

  try {
    const search = report ? `?report=${encodeURIComponent(report)}` : ''
    return await $fetch(`${config.qaApiBase}/ragas${search}`)
  } catch (error) {
    throw createError({
      statusCode: 502,
      statusMessage: 'Impossible de récupérer le rapport RAGAS.',
      data: { error: String(error) }
    })
  }
})
