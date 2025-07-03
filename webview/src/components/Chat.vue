<script setup lang="ts">
import { ref } from 'vue'
import { store } from './store'
import ChatMesage from './ChatMessage.vue'
import ChatForm from './ChatForm.vue'

const loading = ref(false)
const error = ref(null)
const messages = ref([]);

async function onSendUserMessage(content) {
  const message = { "content": content, "role": "user" }

  messages.value.push(message);

  let inferenceResponse = ''

  const mcpClient = store.getMcpClient();
  for await (const response of mcpClient.inference(messages.value)) {
    if (response?.delta?.text) {
        inferenceResponse += response.delta.text;
    }
  };

  if (inferenceResponse) {
    const aiMessage = { "content": inferenceResponse, "role": "assistant" }
    messages.value.push(aiMessage);
  }
}
</script>

<template>
  <div class="chat">
    <div v-if="loading" class="loading">Loading...</div>

    <div v-if="error" class="error">{{ error }}</div>

    <ChatMesage v-for="message in messages" :message="message"/>
    <ChatForm @send-user-message="onSendUserMessage" />
  </div>
</template>
