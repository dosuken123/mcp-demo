<script setup lang="ts">
import { ref, onMounted } from 'vue'
import MyMCPClient from './MyMCPClient'

const isLoading = ref<boolean>(false)
const errorMessage = ref<string>('')
const successMessage = ref<string>('')
const userData = ref<any>(null)
const accessToken = ref<string>('')

// Initialize MCP client
const mcpClient = new MyMCPClient({
  // You can override default config here if needed
  // authorizationEndpoint: 'http://custom-domain/oauth/authorize',
})

// Initiate OAuth flow with PKCE
const initiateOAuthFlow = async (): Promise<void> => {
  try {
    isLoading.value = true;
    errorMessage.value = '';
    
    // Get authorization URL and redirect
    const authUrl = await mcpClient.initiateOAuthFlow();
    window.location.href = authUrl;
    
  } catch (error) {
    console.error('OAuth initialization error:', error);
    errorMessage.value = error instanceof Error ? error.message : String(error);
  } finally {
    isLoading.value = false;
  }
}

// Log user out
const logout = (): void => {
  mcpClient.logout();
  userData.value = null;
  accessToken.value = '';
  successMessage.value = 'Logged out successfully';
}

// Initialize on component mount
onMounted(async (): Promise<void> => {
  isLoading.value = true;
  try {
    // First check if we have an authorization code in the URL (callback from auth server)
    if (window.location.search.includes('code=')) {
      const urlParams = new URLSearchParams(window.location.search);
      const data = await mcpClient.handleOAuthCallback(urlParams);
      
      if (data) {
        userData.value = data;
        accessToken.value = mcpClient.getAccessToken();
        successMessage.value = 'Authentication successful!';
        
        // Clean up URL after successful exchange
        const cleanUrl = window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
      }
    } else {
      // If no authorization code, try to access resource with existing token
      const result = await mcpClient.tryAccessResource();
      
      if (result.success) {
        userData.value = result.userData;
        accessToken.value = mcpClient.getAccessToken();
      } else if (result.error) {
        // Only show error if it's not the "No access token available" error
        if (result.error !== 'No access token available') {
          errorMessage.value = result.error;
        }
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
    <h2>{{ userData ? 'Welcome' : 'MCP Client auth' }}</h2>
    
    <div v-if="errorMessage" style="color: red; margin: 10px 0;">
      {{ errorMessage }}
    </div>
    
    <div v-if="successMessage" style="color: green; margin: 10px 0;">
      {{ successMessage }}
    </div>
    
    <div v-if="isLoading" style="margin: 20px 0;">
      Loading...
    </div>
    
    <!-- OAuth Login Button -->
    <div v-if="!userData && !isLoading">
      <button @click="initiateOAuthFlow" style="background: #4285F4; color: white; border: none; padding: 10px 16px; border-radius: 4px; cursor: pointer; margin-top: 20px;">
        Request access to MCP server with OAuth
      </button>
    </div>
    
    <!-- User Profile -->
    <div v-if="userData">
      <h3>Hello, {{ userData.username || userData.name || 'User' }}</h3>
      
      <div>
        <strong>User Information:</strong>
        <pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; margin-top: 10px;">{{ JSON.stringify(userData, null, 2) }}</pre>
      </div>
      
      <div style="margin-top: 20px;">
        <p><strong>Access Token:</strong></p>
        <div style="background: #f5f5f5; padding: 10px; border-radius: 4px; word-break: break-all; margin-top: 10px;">
          {{ accessToken }}
        </div>
      </div>
      
      <button @click="logout" style="margin-top: 20px; background: #f44336; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
        Logout
      </button>
    </div>
  </div>
</template>
