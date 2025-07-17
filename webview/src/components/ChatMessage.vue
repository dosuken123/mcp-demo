<script setup lang="ts">
import ChatMessageContent from "./ChatMessageContent.vue";

defineProps(["message"]);
</script>

<template>
  <ChatMessageContent
    v-for="content in message.content"
    :content="content"
    :role="message.role"
  />
</template>
