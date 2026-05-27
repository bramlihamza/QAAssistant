<script setup lang="ts">
const route = useRoute()

const links = [
  { to: '/', label: 'User Stories' },
  { to: '/metrics', label: 'Metrics' },
  { to: '/health', label: 'Healthcheck' },
  { to: '/ragas', label: 'RAGAS' }
]
</script>

<template>
  <nav class="app-nav">
    <div class="brand">
      <span class="brand-accent">QA</span>
      <span>Assistant Console</span>
    </div>
    <div class="nav-links">
      <NuxtLink
        v-for="link in links"
        :key="link.to"
        :to="link.to"
        class="nav-link"
        :class="{ active: route.path === link.to }"
      >
        {{ link.label }}
      </NuxtLink>
    </div>
  </nav>
</template>
