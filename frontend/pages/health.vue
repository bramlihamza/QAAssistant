<script setup lang="ts">
import type { HealthResponse } from '~/types/api'

const { data, pending, error, refresh } = await useFetch<HealthResponse>('/api/health')

const statusTone = computed(() => {
  if (!data.value) return 'neutral'
  if (data.value.status === 'ok' && data.value.rag_indexed) return 'good'
  if (data.value.status === 'ok') return 'warn'
  return 'bad'
})
</script>

<template>
  <section class="page-wrap">
    <div class="page-head">
      <h1>Healthcheck</h1>
      <p>État de santé du backend QA et disponibilité du RAG.</p>
    </div>

    <div class="actions-line">
      <button class="btn ghost" @click="refresh()">Rafraîchir</button>
    </div>

    <p v-if="pending" class="state-line">Vérification du healthcheck...</p>
    <p v-else-if="error" class="state-line state-error">Erreur healthcheck: {{ error.message }}</p>

    <article v-else-if="data" class="card health-card" :class="`tone-${statusTone}`">
      <p><strong>Status API:</strong> {{ data.status }}</p>
      <p><strong>RAG Indexed:</strong> {{ data.rag_indexed ? 'true' : 'false' }}</p>
      <p><strong>Model:</strong> {{ data.model }}</p>
      <p><strong>Version:</strong> {{ data.version }}</p>
    </article>
  </section>
</template>
