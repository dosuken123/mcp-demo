<script setup lang="ts">
defineProps(['message']);
</script>

<template>
  <div v-if="message.role == 'user'" class="flex justify-end">
    <div class="bg-blue-200 text-black p-2 rounded-lg max-w-xs">{{ message.content }}</div>
  </div>
  <div v-if="message.role == 'assistant'" class="flex">
    <div class="bg-gray-300 text-black p-2 rounded-lg max-w-xs">{{ message.content }}</div>
  </div>
</template>
