<script setup lang="ts">
import type { MetricsResponse } from '~/types/api'

const { data, pending, error, refresh } = await useFetch<MetricsResponse>('/api/metrics')

const successRate = computed(() => {
  if (!data.value || data.value.requests_total === 0) return 0
  return (data.value.requests_success / data.value.requests_total) * 100
})
</script>

<template>
  <section class="page-wrap">
    <div class="page-head">
      <h1>Metrics API QA</h1>
      <p>Compteurs in-memory depuis le dernier démarrage du backend.</p>
    </div>

    <div class="actions-line">
      <button class="btn ghost" @click="refresh()">Rafraîchir</button>
    </div>

    <p v-if="pending" class="state-line">Chargement des métriques...</p>
    <p v-else-if="error" class="state-line state-error">Erreur métriques: {{ error.message }}</p>

    <div v-else-if="data" class="kpi-grid">
      <article class="card kpi-card">
        <p class="kpi-label">Requests Total</p>
        <p class="kpi-value">{{ data.requests_total }}</p>
      </article>

      <article class="card kpi-card">
        <p class="kpi-label">Requests Success</p>
        <p class="kpi-value">{{ data.requests_success }}</p>
      </article>

      <article class="card kpi-card">
        <p class="kpi-label">Requests Error</p>
        <p class="kpi-value">{{ data.requests_error }}</p>
      </article>

      <article class="card kpi-card">
        <p class="kpi-label">Avg Response (ms)</p>
        <p class="kpi-value">{{ data.avg_response_time_ms }}</p>
      </article>

      <article class="card kpi-card">
        <p class="kpi-label">Test Cases Generated</p>
        <p class="kpi-value">{{ data.test_cases_generated }}</p>
      </article>

      <article class="card kpi-card">
        <p class="kpi-label">Success Rate</p>
        <p class="kpi-value">{{ successRate.toFixed(1) }}%</p>
      </article>
    </div>
  </section>
</template>
