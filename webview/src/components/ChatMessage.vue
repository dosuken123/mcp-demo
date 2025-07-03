<script setup lang="ts">
defineProps(['message']);
</script>

<template>
  <div class="chat_message">
    <p>{{ message }}</p>
  </div>
</template>
