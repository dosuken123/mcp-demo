<script setup lang="ts">
import { onMounted } from 'vue'
import Login from './components/Login.vue'
import Logout from './components/Logout.vue'
import Chat from './components/Chat.vue'
import Tools from './components/Tools.vue'
import { store } from './components/store'

onMounted(async (): Promise<void> => {
  store.updateHasValidAccessToken(
    !!await store.getMcpClient().getAccessToken()
  );
});
</script>

<style>
@import './components/style.css';
</style>

<template>
  <div v-if="store.hasValidAccessToken">
    <Chat />
    <Tools />
    <Logout />
  </div>
  <div v-else>
    <Login />
  </div>
</template>
