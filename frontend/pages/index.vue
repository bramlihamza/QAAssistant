<script setup lang="ts">
import type { AskResponse, UserStory } from '~/types/api'

const search = ref('')
const priority = ref<'all' | 'high' | 'medium' | 'low'>('all')
const status = ref<'all' | 'ready' | 'draft' | 'in-progress' | 'done'>('all')

const activeIndex = ref<string | null>(null)
const generationError = ref('')
const generationState = reactive<Record<string, AskResponse>>({})

const {
  data: stories,
  pending,
  error,
  refresh
} = await useFetch<UserStory[]>('/api/user-stories', {
  default: () => []
})

function extractStoriesCollection(payload: unknown): unknown[] {
  if (Array.isArray(payload)) {
    return payload
  }

  if (typeof payload === 'string') {
    try {
      const parsed = JSON.parse(payload)
      return Array.isArray(parsed) ? parsed : []
    } catch {
      return []
    }
  }

  if (payload && typeof payload === 'object') {
    const record = payload as Record<string, unknown>

    // Common wrapper keys
    for (const key of ['data', 'items', 'stories', 'userStories', 'results']) {
      if (Array.isArray(record[key])) {
        return record[key] as unknown[]
      }
    }

    // Fallback: first array field found
    for (const value of Object.values(record)) {
      if (Array.isArray(value)) {
        return value as unknown[]
      }
    }

    // Object map fallback: {"1": {...}, "2": {...}}
    const objectValues = Object.values(record).filter(
      (value) => Boolean(value) && typeof value === 'object'
    )
    if (objectValues.length > 0) {
      return objectValues
    }
  }

  return []
}

const normalizedStories = computed<UserStory[]>(() => {
  const rawStories = extractStoriesCollection(stories.value)

  return rawStories
    .filter((item): item is Partial<UserStory> => Boolean(item) && typeof item === 'object')
    .map((story, idx) => ({
      id: typeof story.id === 'number' ? story.id : idx + 1,
      index: typeof story.index === 'string' ? story.index : `US-${String(idx + 1).padStart(3, '0')}`,
      title: typeof story.title === 'string' ? story.title : 'Sans titre',
      description: typeof story.description === 'string' ? story.description : '',
      constraints: Array.isArray(story.constraints)
        ? story.constraints.filter((value): value is string => typeof value === 'string')
        : [],
      acceptanceCriteria: Array.isArray(story.acceptanceCriteria)
        ? story.acceptanceCriteria.filter((value): value is string => typeof value === 'string')
        : [],
      priority:
        story.priority === 'high' || story.priority === 'medium' || story.priority === 'low'
          ? story.priority
          : 'medium',
      status:
        story.status === 'draft' ||
        story.status === 'ready' ||
        story.status === 'in-progress' ||
        story.status === 'done'
          ? story.status
          : 'draft',
      images: Array.isArray(story.images)
        ? story.images.filter((value): value is string => typeof value === 'string')
        : []
    }))
})

const effectivePriority = computed<'all' | 'high' | 'medium' | 'low'>(() => {
  return priority.value === 'high' || priority.value === 'medium' || priority.value === 'low'
    ? priority.value
    : 'all'
})

const effectiveStatus = computed<'all' | 'ready' | 'draft' | 'in-progress' | 'done'>(() => {
  return status.value === 'ready' ||
    status.value === 'draft' ||
    status.value === 'in-progress' ||
    status.value === 'done'
    ? status.value
    : 'all'
})

const filteredStories = computed(() => {
  const normalizedSearch = search.value.trim().toLowerCase()
  const list = normalizedStories.value

  return list
    .filter((story) => {
      if (effectivePriority.value !== 'all' && story.priority !== effectivePriority.value) return false
      if (effectiveStatus.value !== 'all' && story.status !== effectiveStatus.value) return false

      if (!normalizedSearch) return true

      return [story.index, story.title, story.description]
        .join(' ')
        .toLowerCase()
        .includes(normalizedSearch)
    })
    .sort((a, b) => a.id - b.id)
})

const isGenerating = computed(() => activeIndex.value !== null)

function priorityClass(p: string) {
  return `badge priority-${p}`
}

function statusClass(s: string) {
  return `badge status-${s}`
}

async function generateFor(story: UserStory) {
  generationError.value = ''
  activeIndex.value = story.index

  try {
    const result = await $fetch<AskResponse>('/api/generate', {
      method: 'POST',
      body: {
        index: story.index,
        story: {
          index: story.index,
          title: story.title,
          description: story.description,
          constraints: story.constraints,
          acceptanceCriteria: story.acceptanceCriteria,
          priority: story.priority,
          status: story.status
        }
      }
    })

    generationState[story.index] = result
  } catch (err) {
    generationError.value = err instanceof Error ? err.message : 'Erreur inattendue pendant la génération.'
  } finally {
    activeIndex.value = null
  }
}
</script>

<template>
  <section class="page-wrap">
    <div class="page-head">
      <h1>User Stories & Génération de Tests</h1>
      <p>Source: <code>mickaellherminez/github-user-stories-fake-api</code> consommée via l'agent QA.</p>
    </div>

    <div class="toolbar card">
      <div class="toolbar-group">
        <label for="search">Recherche</label>
        <input id="search" v-model="search" type="text" placeholder="US-006, login, rendez-vous..." />
      </div>

      <div class="toolbar-group">
        <label for="priority">Priorité</label>
        <select id="priority" v-model="priority">
          <option value="all">Toutes</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      <div class="toolbar-group">
        <label for="status">Statut</label>
        <select id="status" v-model="status">
          <option value="all">Tous</option>
          <option value="ready">Ready</option>
          <option value="draft">Draft</option>
          <option value="in-progress">In Progress</option>
          <option value="done">Done</option>
        </select>
      </div>

      <button class="btn ghost" @click="refresh()">Rafraîchir</button>
    </div>

    <p v-if="pending" class="state-line">Chargement des user stories...</p>
    <p v-else-if="error" class="state-line state-error">Impossible de charger les user stories: {{ error.message }}</p>
    <p v-else class="state-line">{{ filteredStories.length }} user stories affichées</p>

    <p v-if="generationError" class="state-line state-error">{{ generationError }}</p>

    <div class="stories-grid">
      <article v-for="story in filteredStories" :key="story.id" class="card story-card">
        <div class="story-head">
          <div>
            <p class="story-index">{{ story.index }}</p>
            <h2>{{ story.title }}</h2>
          </div>
          <div class="badges">
            <span :class="priorityClass(story.priority)">{{ story.priority }}</span>
            <span :class="statusClass(story.status)">{{ story.status }}</span>
          </div>
        </div>

        <p class="story-description">{{ story.description }}</p>

        <div class="criteria-wrap">
          <p class="criteria-title">Acceptance Criteria</p>
          <ul>
            <li v-for="criterion in story.acceptanceCriteria.slice(0, 3)" :key="criterion">{{ criterion }}</li>
          </ul>
        </div>

        <div class="actions">
          <button
            class="btn"
            :disabled="isGenerating"
            @click="generateFor(story)"
          >
            <span v-if="activeIndex === story.index">Génération...</span>
            <span v-else>Générer les tests</span>
          </button>
        </div>

        <div v-if="generationState[story.index]" class="result-block">
          <p class="result-title">Réponse agent</p>
          <p class="result-answer">{{ generationState[story.index].answer }}</p>
          <p class="result-meta">
            Intent: <code>{{ generationState[story.index].intent }}</code> ·
            Test cases: <code>{{ generationState[story.index].test_cases.length }}</code>
          </p>
          <details>
            <summary>Voir les cas de test générés</summary>
            <div class="test-cases">
              <article v-for="tc in generationState[story.index].test_cases" :key="tc.id" class="test-case">
                <h3>{{ tc.id }} — {{ tc.titre }}</h3>
                <p><strong>Catégorie:</strong> {{ tc.catégorie }} · <strong>Priorité:</strong> {{ tc.priorité }}</p>
                <p><strong>Préconditions:</strong> {{ tc.préconditions }}</p>
                <p><strong>Résultat attendu:</strong> {{ tc.résultat_attendu }}</p>
              </article>
            </div>
          </details>
        </div>
      </article>
    </div>
  </section>
</template>
