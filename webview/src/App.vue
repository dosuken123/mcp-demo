<script setup lang="ts">
import { onMounted } from 'vue'
import Login from './components/Login.vue'
import Logout from './components/Logout.vue'
import Chat from './components/Chat.vue'
import { store } from './components/store'

onMounted(async (): Promise<void> => {
  store.updateHasValidAccessToken(
    !!store.getMcpClient().getAccessToken()
  );
});
</script>

<template>
  <header>
    <h1>Chat app (MCP Host)</h1>
  </header>

  <div v-if="store.hasValidAccessToken">
    <Chat />
    <Logout />
  </div>
  <div v-else>
    <Login />
  </div>
</template>
