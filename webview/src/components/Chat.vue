<template>
  <div class="chat">
    <div v-if="loading" class="loading">Loading...</div>

    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="post" class="content">
        <h2>{{ post.title }}</h2>
        <p>{{ post.body }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const loading = ref(false)
const post = ref(null)
const error = ref(null)

watch(() => '1', fetchData, { immediate: true })

async function fetchData(id) {
    error.value = post.value = null
    loading.value = true

    try {
        const response = await fetch('http://localhost:8000/inference', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer test`,
            },
            body: JSON.stringify({"test": "test"})
        });

        post.value = response
    } catch (err) {
        error.value = err.message
    } finally {
        loading.value = false
    }
}
</script>