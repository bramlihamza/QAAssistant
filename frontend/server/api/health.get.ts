import { createError } from 'h3'

export default defineEventHandler(async () => {
  const config = useRuntimeConfig()

  try {
    return await $fetch(`${config.qaApiBase}/health`)
  } catch (error) {
    throw createError({
      statusCode: 502,
      statusMessage: 'Impossible de récupérer le healthcheck QA.',
      data: { error: String(error) }
    })
  }
})
