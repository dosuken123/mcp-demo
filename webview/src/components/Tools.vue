<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { store } from './store'

onMounted(async () => {
  const mcpClient = store.getMcpClient();
  const tools = await mcpClient.getTools();
  store.updateMcpTools(tools);
})
</script>

<template>
  <p>{{ store.mcpTools }}</p>
</template>
