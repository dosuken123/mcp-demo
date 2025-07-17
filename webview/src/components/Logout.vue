<script setup lang="ts">
import { store } from "./store";

// Log user out
const logout = (): void => {
  store.getMcpClient().logout();
};
</script>

<template>
  <div>
    <button
      @click="logout"
      style="
        margin-top: 20px;
        background: #f44336;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
      "
    >
      Logout
    </button>
  </div>
</template>
