<script setup>
import { ref, onMounted } from 'vue'

const username = ref('')
const password = ref('')
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const userData = ref(null)
const accessToken = ref('')
const codeVerifier = ref('')
const codeChallenge = ref('')
const state = ref('')

// OAuth config
const oauthConfig = {
  authorizationEndpoint: 'http://localhost:8000/oauth/authorize',
  tokenEndpoint: 'http://localhost:8000/oauth/token',
  clientId: 'your-client-id', // Replace with your client ID
  redirectUri: window.location.origin + '/callback', // Adjust as needed
  scope: 'read write', // Adjust scopes as needed
  resourceEndpoint: 'http://localhost:8000/users/me/',
}

// Generate a random string of specified length
const generateRandomString = (length) => {
  const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
  let text = '';
  for (let i = 0; i < length; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
}

// Generate code verifier and challenge
const generateCodeChallenge = async () => {
  // Generate code verifier (random string between 43-128 chars)
  const newCodeVerifier = generateRandomString(64);
  codeVerifier.value = newCodeVerifier;
  
  // Create code challenge using SHA-256
  const encoder = new TextEncoder();
  const data = encoder.encode(newCodeVerifier);
  const digest = await window.crypto.subtle.digest('SHA-256', data);
  
  // Convert to base64-url format (base64 without padding, replacing '+' with '-', '/' with '_')
  const base64Digest = btoa(String.fromCharCode(...new Uint8Array(digest)))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
  
  codeChallenge.value = base64Digest;
  return base64Digest;
}

// Try to access protected resource first
const tryAccessResource = async () => {
  try {
    const token = localStorage.getItem('oauth_access_token');
    
    if (!token) {
      throw new Error('No access token available');
    }
    
    accessToken.value = token;
    const response = await fetch(oauthConfig.resourceEndpoint, {
      method: 'GET',
      headers: {
        'accept': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.status === 401) {
      // Token expired or invalid, try refresh token first
      const refreshToken = localStorage.getItem('oauth_refresh_token');
      if (refreshToken) {
        const refreshed = await refreshAccessToken(refreshToken);
        if (refreshed) {
          return await tryAccessResource(); // Try again with new token
        }
      }
      
      // If refresh failed or no refresh token, initiate auth flow
      await initiateOAuthFlow();
      return false;
    }
    
    if (!response.ok) {
      throw new Error('Failed to fetch user data');
    }
    
    const data = await response.json();
    userData.value = data;
    return true;
    
  } catch (error) {
    console.error('Error accessing resource:', error);
    
    // Initiate OAuth flow if no token or other error
    if (error.message === 'No access token available') {
      await initiateOAuthFlow();
    } else {
      errorMessage.value = error.message;
    }
    return false;
  }
}

// Initiate OAuth flow with PKCE
const initiateOAuthFlow = async () => {
  try {
    isLoading.value = true;
    
    // Generate PKCE code verifier and challenge
    await generateCodeChallenge();
    
    // Generate and store state for CSRF protection
    state.value = generateRandomString(32);
    localStorage.setItem('oauth_state', state.value);
    localStorage.setItem('oauth_code_verifier', codeVerifier.value);
    
    // Construct authorization URL
    const authUrl = new URL(oauthConfig.authorizationEndpoint);
    authUrl.searchParams.append('response_type', 'code');
    authUrl.searchParams.append('client_id', oauthConfig.clientId);
    authUrl.searchParams.append('redirect_uri', oauthConfig.redirectUri);
    authUrl.searchParams.append('scope', oauthConfig.scope);
    authUrl.searchParams.append('state', state.value);
    authUrl.searchParams.append('code_challenge', codeChallenge.value);
    authUrl.searchParams.append('code_challenge_method', 'S256');
    
    // Open authorization URL in current window
    window.location.href = authUrl.toString();
    
  } catch (error) {
    console.error('OAuth initialization error:', error);
    errorMessage.value = 'Failed to start authentication process: ' + error.message;
    isLoading.value = false;
  }
}

// Exchange authorization code for tokens
const exchangeCodeForToken = async (code) => {
  try {
    isLoading.value = true;
    
    // Get stored code verifier
    const storedCodeVerifier = localStorage.getItem('oauth_code_verifier');
    if (!storedCodeVerifier) {
      throw new Error('Code verifier not found');
    }
    
    const params = new URLSearchParams();
    params.append('grant_type', 'authorization_code');
    params.append('code', code);
    params.append('redirect_uri', oauthConfig.redirectUri);
    params.append('client_id', oauthConfig.clientId);
    params.append('code_verifier', storedCodeVerifier);
    
    const response = await fetch(oauthConfig.tokenEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: params
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error_description || data.error || 'Failed to exchange code for token');
    }
    
    // Save tokens
    accessToken.value = data.access_token;
    localStorage.setItem('oauth_access_token', data.access_token);
    
    if (data.refresh_token) {
      localStorage.setItem('oauth_refresh_token', data.refresh_token);
    }
    
    // Clear PKCE and state values
    localStorage.removeItem('oauth_code_verifier');
    localStorage.removeItem('oauth_state');
    
    successMessage.value = 'Authentication successful!';
    
    // Fetch user data with new token
    await fetchUserData();
    return true;
    
  } catch (error) {
    console.error('Token exchange error:', error);
    errorMessage.value = error.message;
    return false;
  } finally {
    isLoading.value = false;
  }
}

// Refresh the access token using a refresh token
const refreshAccessToken = async (refreshToken) => {
  try {
    const params = new URLSearchParams();
    params.append('grant_type', 'refresh_token');
    params.append('refresh_token', refreshToken);
    params.append('client_id', oauthConfig.clientId);
    
    const response = await fetch(oauthConfig.tokenEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: params
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      // If refresh fails, clear tokens and return false
      localStorage.removeItem('oauth_access_token');
      localStorage.removeItem('oauth_refresh_token');
      return false;
    }
    
    // Save new tokens
    accessToken.value = data.access_token;
    localStorage.setItem('oauth_access_token', data.access_token);
    
    if (data.refresh_token) {
      localStorage.setItem('oauth_refresh_token', data.refresh_token);
    }
    
    return true;
    
  } catch (error) {
    console.error('Token refresh error:', error);
    return false;
  }
}

// Fetch user data with current token
const fetchUserData = async () => {
  try {
    const token = accessToken.value || localStorage.getItem('oauth_access_token');
    
    if (!token) {
      throw new Error('No access token available');
    }
    
    const response = await fetch(oauthConfig.resourceEndpoint, {
      method: 'GET',
      headers: {
        'accept': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || data.message || 'Failed to fetch user data');
    }
    
    userData.value = data;
    
  } catch (error) {
    console.error('Error fetching user data:', error);
    errorMessage.value = error.message;
  }
}

// Log user out
const logout = () => {
  userData.value = null;
  accessToken.value = '';
  localStorage.removeItem('oauth_access_token');
  localStorage.removeItem('oauth_refresh_token');
  successMessage.value = 'Logged out successfully';
}

// Handle OAuth callback
const handleOAuthCallback = () => {
  // Check if current URL contains authorization code
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get('code');
  const returnedState = urlParams.get('state');
  const error = urlParams.get('error');
  
  if (error) {
    errorMessage.value = `Authorization error: ${error}`;
    return;
  }
  
  if (code) {
    // Verify state to prevent CSRF
    const storedState = localStorage.getItem('oauth_state');
    if (returnedState !== storedState) {
      errorMessage.value = 'State mismatch. Possible CSRF attack.';
      return;
    }
    
    // Exchange code for token
    exchangeCodeForToken(code).then(() => {
      // Clean up URL after successful exchange
      const cleanUrl = window.location.pathname;
      window.history.replaceState({}, document.title, cleanUrl);
    });
  }
}

// Initialize on component mount
onMounted(async () => {
  // First check if we have an authorization code in the URL (callback from auth server)
  handleOAuthCallback();
  
  // If no authorization code, try to access resource with existing token
  if (!window.location.search.includes('code=')) {
    await tryAccessResource();
  }
});
</script>

<template>
  <div>
    <h2>{{ userData ? 'Welcome' : 'OAuth Authentication' }}</h2>
    
    <div v-if="errorMessage" style="color: red; margin: 10px 0;">
      {{ errorMessage }}
    </div>
    
    <div v-if="successMessage" style="color: green; margin: 10px 0;">
      {{ successMessage }}
    </div>
    
    <div v-if="isLoading" style="margin: 20px 0;">
      Loading...
    </div>
    
    <!-- Manual Login Button (as fallback) -->
    <div v-if="!userData && !isLoading">
      <button @click="initiateOAuthFlow" style="background: #4285F4; color: white; border: none; padding: 10px 16px; border-radius: 4px; cursor: pointer; margin-top: 20px;">
        Sign in with OAuth
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