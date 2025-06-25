/**
 * Configuration options for OAuth client
 */
export interface OAuthConfig {
  authorizationEndpoint: string;
  tokenEndpoint: string;
  clientId: string;
  redirectUri: string;
  resource: string;
  scope: string;
  resourceEndpoint: string;
}

/**
 * Result of resource access attempt
 */
export interface ResourceAccessResult {
  success: boolean;
  toolData?: any;
  error?: string;
}

/**
 * MyMCPClient handles OAuth 2.0 authentication flow with PKCE
 */
export default class MyMCPClient {
  private config: OAuthConfig;
  private accessToken: string;
  private codeVerifier: string;
  private codeChallenge: string;
  private state: string;

  /**
   * Creates a new MyMCPClient instance
   * @param config Configuration options
   */
  constructor(config: Partial<OAuthConfig>) {
    // Default configuration with optional overrides
    this.config = {
      authorizationEndpoint: 'http://localhost:8000/oauth/authorize',
      tokenEndpoint: 'http://localhost:8000/oauth/token',
      clientId: 'my-mcp-client',
      redirectUri: window.location.origin + '/callback',
      resource: 'http://localhost:8000',
      scope: 'read write',
      resourceEndpoint: 'http://localhost:8000/mcp',
      ...config
    };
    
    this.accessToken = localStorage.getItem('oauth_access_token') || '';
    this.codeVerifier = '';
    this.codeChallenge = '';
    this.state = '';
  }

  /**
   * Generates a random string of specified length
   * @param length Length of the string to generate
   * @returns Random string
   */
  private generateRandomString(length: number): string {
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
    let text = '';
    for (let i = 0; i < length; i++) {
      text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
  }

  /**
   * Generates PKCE code verifier and challenge
   * @returns Promise resolving to the code challenge
   */
  private async generateCodeChallenge(): Promise<string> {
    // Generate code verifier (random string between 43-128 chars)
    const newCodeVerifier = this.generateRandomString(64);
    this.codeVerifier = newCodeVerifier;
    
    // Create code challenge using SHA-256
    const encoder = new TextEncoder();
    const data = encoder.encode(newCodeVerifier);
    const digest = await window.crypto.subtle.digest('SHA-256', data);
    
    // Convert to base64-url format
    const base64Digest = btoa(String.fromCharCode(...new Uint8Array(digest)))
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '');
    
    this.codeChallenge = base64Digest;
    return base64Digest;
  }

  /**
   * Attempts to access a protected resource with existing token
   * @returns Promise resolving to access result
   */
  public async tryAccessResource(): Promise<ResourceAccessResult> {
    try {
      const token = localStorage.getItem('oauth_access_token');
      
      if (!token) {
        throw new Error('No access token available');
      }
      
      this.accessToken = token;
      const response = await fetch(this.config.resourceEndpoint, {
        method: 'POST',
        headers: {
          'accept': 'application/json, text/event-stream',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'MCP-Protocol-Version': '2025-06-18',
        },
        body: JSON.stringify({
          jsonrpc: '2.0',
          id: 1,
          method: 'tools/list'
        })
      });
      
      if (response.status === 401) {
        // Token expired or invalid, try refresh token first
        const refreshToken = localStorage.getItem('oauth_refresh_token');
        if (refreshToken) {
          const refreshed = await this.refreshAccessToken(refreshToken);
          if (refreshed) {
            return await this.tryAccessResource(); // Try again with new token
          }
        }
        
        return { success: false };
      }
      
      if (response.status != 202) {
        throw new Error('Failed to fetch tool data');
      }
      
      const data = await response.json();
      return { success: true, toolData: data };
      
    } catch (error) {
      console.error('Error accessing resource:', error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : String(error)
      };
    }
  }

  /**
   * Initiates OAuth flow with PKCE
   * @returns Promise resolving to the authorization URL
   */
  public async initiateOAuthFlow(): Promise<string> {
    try {
      // Generate PKCE code verifier and challenge
      await this.generateCodeChallenge();
      
      // Generate and store state for CSRF protection
      this.state = this.generateRandomString(32);
      localStorage.setItem('oauth_state', this.state);
      localStorage.setItem('oauth_code_verifier', this.codeVerifier);
      
      // Construct authorization URL
      const authUrl = new URL(this.config.authorizationEndpoint);
      authUrl.searchParams.append('response_type', 'code');
      authUrl.searchParams.append('client_id', this.config.clientId);
      authUrl.searchParams.append('redirect_uri', this.config.redirectUri);
      authUrl.searchParams.append('resource', this.config.resource);
      authUrl.searchParams.append('scope', this.config.scope);
      authUrl.searchParams.append('state', this.state);
      authUrl.searchParams.append('code_challenge', this.codeChallenge);
      authUrl.searchParams.append('code_challenge_method', 'S256');
      
      // Return the URL for the component to handle navigation
      return authUrl.toString();
      
    } catch (error) {
      console.error('OAuth initialization error:', error);
      throw new Error('Failed to start authentication process: ' + 
        (error instanceof Error ? error.message : String(error)));
    }
  }

  /**
   * Exchanges authorization code for access tokens
   * @param code Authorization code from OAuth server
   * @returns Promise resolving to user data
   */
  public async exchangeCodeForToken(code: string): Promise<any> {
    try {
      // Get stored code verifier
      const storedCodeVerifier = localStorage.getItem('oauth_code_verifier');
      if (!storedCodeVerifier) {
        throw new Error('Code verifier not found');
      }
      
      const params = new URLSearchParams();
      params.append('grant_type', 'authorization_code');
      params.append('code', code);
      params.append('redirect_uri', this.config.redirectUri);
      params.append('resource', this.config.resource);
      params.append('client_id', this.config.clientId);
      params.append('code_verifier', storedCodeVerifier);
      
      const response = await fetch(this.config.tokenEndpoint, {
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
      this.accessToken = data.access_token;
      localStorage.setItem('oauth_access_token', data.access_token);
      
      if (data.refresh_token) {
        localStorage.setItem('oauth_refresh_token', data.refresh_token);
      }
      
      // Clear PKCE and state values
      localStorage.removeItem('oauth_code_verifier');
      localStorage.removeItem('oauth_state');
      
      // Fetch tool data with new token
      const toolData = await this.tryAccessResource();
      return toolData;
      
    } catch (error) {
      console.error('Token exchange error:', error);
      throw error;
    }
  }

  /**
   * Refreshes access token using refresh token
   * @param refreshToken Refresh token from previous authentication
   * @returns Promise resolving to success status
   */
  public async refreshAccessToken(refreshToken: string): Promise<boolean> {
    try {
      const params = new URLSearchParams();
      params.append('grant_type', 'refresh_token');
      params.append('refresh_token', refreshToken);
      params.append('client_id', this.config.clientId);
      
      const response = await fetch(this.config.tokenEndpoint, {
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
      this.accessToken = data.access_token;
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

  /**
   * Handles OAuth callback with authorization code
   * @param urlParams URL search params containing authorization code
   * @returns Promise resolving to user data or null
   */
  public async handleOAuthCallback(urlParams: URLSearchParams): Promise<any | null> {
    const code = urlParams.get('code');
    const returnedState = urlParams.get('state');
    const error = urlParams.get('error');
    
    if (error) {
      throw new Error(`Authorization error: ${error}`);
    }
    
    if (code && returnedState) {
      // Verify state to prevent CSRF
      const storedState = localStorage.getItem('oauth_state');
      if (returnedState !== storedState) {
        throw new Error('State mismatch. Possible CSRF attack.');
      }
      
      // Exchange code for token
      return await this.exchangeCodeForToken(code);
    }
    
    return null;
  }

  /**
   * Logs user out by clearing tokens
   * @returns Success status
   */
  public logout(): boolean {
    this.accessToken = '';
    localStorage.removeItem('oauth_access_token');
    localStorage.removeItem('oauth_refresh_token');
    return true;
  }

  /**
   * Gets current access token
   * @returns Access token string
   */
  public getAccessToken(): string {
    return this.accessToken || localStorage.getItem('oauth_access_token') || '';
  }
}
