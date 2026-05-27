export default defineNuxtConfig({
  compatibilityDate: '2026-05-27',
  devtools: { enabled: false },
  ssr: true,
  css: ['~/assets/css/main.css'],
  app: {
    head: {
      title: 'QA Assistant Console',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content: 'Console QA pour visualiser les User Stories, générer des tests, et suivre les métriques RAGAS/health.'
        }
      ],
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap'
        }
      ]
    }
  },
  runtimeConfig: {
    // API sur le même domaine Vercel (optionnel, peut être surchargé par env)
    qaApiBase: process.env.QA_API_BASE || '/api',
    userStoriesApiBase:
      process.env.USER_STORIES_API_BASE ||
      'https://raw.githubusercontent.com/mickaellherminez/github-user-stories-fake-api/main/data',
    public: {
      appName: 'QA Assistant Console',
      apiBase: process.env.PUBLIC_API_BASE || '/api'
    }
  }
})
