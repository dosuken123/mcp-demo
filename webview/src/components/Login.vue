<script setup lang="ts">
import { ref, onMounted } from "vue";
import { store } from "./store";
import MCPClient from "./MCPClient";

const isLoading = ref<boolean>(false);
const errorMessage = ref<string>("");
const successMessage = ref<string>("");

// Initiate OAuth flow with PKCE
const initiateOAuthFlow = async (): Promise<void> => {
  try {
    isLoading.value = true;
    errorMessage.value = "";

    // Get authorization URL and redirect
    const authUrl = await store.getMcpClient().initiateOAuthFlow();
    window.location.href = authUrl;
  } catch (error) {
    console.error("OAuth initialization error:", error);
    errorMessage.value = error instanceof Error ? error.message : String(error);
  } finally {
    isLoading.value = false;
  }
};

// Initialize on component mount
onMounted(async (): Promise<void> => {
  isLoading.value = true;
  try {
    // First check if we have an authorization code in the URL (callback from auth server)
    if (window.location.search.includes("code=")) {
      const urlParams = new URLSearchParams(window.location.search);
      const result = await store.getMcpClient().handleOAuthCallback(urlParams);

      if (result) {
        successMessage.value = "Authentication successful!";

        // Clean up URL after successful exchange
        const cleanUrl = window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
      }
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : String(error);
  } finally {
    isLoading.value = false;
  }
});
</script>

<template>
  <div>
    <h2>{{ "Login with OAuth" }}</h2>

    <div v-if="errorMessage" style="color: red; margin: 10px 0">
      {{ errorMessage }}
    </div>

    <div v-if="successMessage" style="color: green; margin: 10px 0">
      {{ successMessage }}
    </div>

    <div v-if="isLoading" style="margin: 20px 0">Loading...</div>

    <div v-if="!isLoading">
      <button
        @click="initiateOAuthFlow"
        style="
          background: #4285f4;
          color: white;
          border: none;
          padding: 10px 16px;
          border-radius: 4px;
          cursor: pointer;
          margin-top: 20px;
        "
      >
        Request access to backend server (MCP + inference) with OAuth
      </button>
    </div>
  </div>
</template>
