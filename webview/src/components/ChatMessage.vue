<script setup lang="ts">
import AssistantMessage from "./messages/AssistantMessage.vue";
import UserMessage from "./messages/UserMessage.vue";

defineProps(["message"]);
</script>

<template>
  <assistant-message v-if="message.role == 'assistant'" :message="message" />
  <user-message v-if="message.role == 'user'" :message="message" />
</template>
