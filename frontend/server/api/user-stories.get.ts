import { createError } from 'h3'

export default defineEventHandler(async () => {
  const config = useRuntimeConfig()

  try {
    const fromQa = await $fetch<unknown>(`${config.qaApiBase}/user-stories`)

    // Validate shape and fallback when backend returns an empty list.
    if (Array.isArray(fromQa) && fromQa.length > 0) {
      return fromQa
    }
  } catch {
    // no-op: fallback handled below
  }

  try {
    return await $fetch(`${config.userStoriesApiBase}/user-stories.json`)
  } catch (rawError) {
    throw createError({
      statusCode: 502,
      statusMessage: 'Impossible de charger les user stories depuis le backend QA ou GitHub Raw.',
      data: {
        rawError: String(rawError)
      }
    })
  }
})
