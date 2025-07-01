<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { store } from './store'

const route = useRoute()
const loading = ref(false)
const error = ref(null)
const inferenceResponse = ref('')

onMounted(async (): Promise<void> => {
  const mcpClient = store.getMcpClient();
  for await (const response of mcpClient.inference()) {
    if (response?.delta?.text) {
        inferenceResponse.value += response.delta.text;
    }
  };
});
</script>

<template>
  <div class="chat">
    <div v-if="loading" class="loading">Loading...</div>

    <div v-if="error" class="error">{{ error }}</div>

    <p>{{ inferenceResponse }}</p>
  </div>
</template>
