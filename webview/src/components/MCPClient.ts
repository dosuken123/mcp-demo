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
  mcpEndpoint: string;
  inferenceEndpoint: string;
}

export type MessageContent = {
  type: string;
  text: string;
  id: string; // For tool use in assistant message
  name: string; // For tool use in assistant message
  input: object; // For tool use in assistant message
  inputBuffer: string; // For stremable input
  tool_use_id: string; // For tool result in user message
  content: string; // For tool result in user message
};

export type Message = {
  content: Array<MessageContent>;
  role: string;
};

export type Tool = {
  name: string;
  id: string;
  inputJson: string;
};

import { store } from "./store";

/**
 * MCPClient handles OAuth 2.0 authentication flow with PKCE
 */
export default class MCPClient {
  private config: OAuthConfig;
  private accessToken: string;
  private codeVerifier: string;
  private codeChallenge: string;
  private state: string;

  /**
   * Creates a new MCPClient instance
   * @param config Configuration options
   */
  constructor(config: Partial<OAuthConfig>) {
    // Default configuration with optional overrides
    this.config = {
      authorizationEndpoint: "http://localhost:8000/oauth/authorize",
      tokenEndpoint: "http://localhost:8000/oauth/token",
      clientId: "my-mcp-client",
      redirectUri: window.location.origin + "/callback",
      resource: "http://localhost:8000",
      scope: "read write",
      mcpEndpoint: "http://localhost:8000/mcp",
      inferenceEndpoint: "http://localhost:8000/inference",
      ...config,
    };

    this.accessToken = localStorage.getItem("oauth_access_token") || "";
    this.codeVerifier = "";
    this.codeChallenge = "";
    this.state = "";
  }

  /**
   * Generates a random string of specified length
   * @param length Length of the string to generate
   * @returns Random string
   */
  private generateRandomString(length: number): string {
    const possible =
      "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~";
    let text = "";
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
    const digest = await window.crypto.subtle.digest("SHA-256", data);

    // Convert to base64-url format
    const base64Digest = btoa(String.fromCharCode(...new Uint8Array(digest)))
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/, "");

    this.codeChallenge = base64Digest;
    return base64Digest;
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
      localStorage.setItem("oauth_state", this.state);
      localStorage.setItem("oauth_code_verifier", this.codeVerifier);

      // Construct authorization URL
      const authUrl = new URL(this.config.authorizationEndpoint);
      authUrl.searchParams.append("response_type", "code");
      authUrl.searchParams.append("client_id", this.config.clientId);
      authUrl.searchParams.append("redirect_uri", this.config.redirectUri);
      authUrl.searchParams.append("resource", this.config.resource);
      authUrl.searchParams.append("scope", this.config.scope);
      authUrl.searchParams.append("state", this.state);
      authUrl.searchParams.append("code_challenge", this.codeChallenge);
      authUrl.searchParams.append("code_challenge_method", "S256");

      // Return the URL for the component to handle navigation
      return authUrl.toString();
    } catch (error) {
      console.error("OAuth initialization error:", error);
      throw new Error(
        "Failed to start authentication process: " +
          (error instanceof Error ? error.message : String(error)),
      );
    }
  }

  /**
   * Generate OAuth access token from authorization code
   * @param code Authorization code from OAuth server
   * @returns Promise resolving to user data
   */
  public async generateToken(code: string): Promise<any> {
    try {
      // Get stored code verifier
      const storedCodeVerifier = localStorage.getItem("oauth_code_verifier");
      if (!storedCodeVerifier) {
        throw new Error("Code verifier not found");
      }

      const params = new URLSearchParams();
      params.append("grant_type", "authorization_code");
      params.append("code", code);
      params.append("redirect_uri", this.config.redirectUri);
      params.append("resource", this.config.resource);
      params.append("client_id", this.config.clientId);
      params.append("code_verifier", storedCodeVerifier);

      const response = await fetch(this.config.tokenEndpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: params,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error_description ||
            data.error ||
            "Failed to exchange code for token",
        );
      }

      // Save tokens
      this.accessToken = data.access_token;
      const expires_at = this.currentEpochTime() + data.expires_in;
      store.updateHasValidAccessToken(true);
      localStorage.setItem("oauth_access_token", data.access_token);
      localStorage.setItem("oauth_access_token_expires_at", expires_at);

      if (data.refresh_token) {
        localStorage.setItem("oauth_refresh_token", data.refresh_token);
      }

      // Clear PKCE and state values
      localStorage.removeItem("oauth_code_verifier");
      localStorage.removeItem("oauth_state");

      return this.accessToken;
    } catch (error) {
      console.error("Token exchange error:", error);
      throw error;
    }
  }

  /**
   * Refreshes access token using refresh token
   * @param refreshToken Refresh token from previous authentication
   * @returns Promise resolving to success status
   */
  public async refreshAccessToken(refreshToken: string): Promise<any> {
    try {
      const params = new URLSearchParams();
      params.append("grant_type", "refresh_token");
      params.append("refresh_token", refreshToken);
      params.append("client_id", this.config.clientId);

      const response = await fetch(this.config.tokenEndpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: params,
      });

      const data = await response.json();

      if (!response.ok) {
        // If refresh fails, clear tokens and return false
        localStorage.removeItem("oauth_access_token");
        localStorage.removeItem("oauth_refresh_token");
        return false;
      }

      // Save new tokens
      this.accessToken = data.access_token;
      const expires_at = this.currentEpochTime() + data.expires_in;
      localStorage.setItem("oauth_access_token", data.access_token);
      localStorage.setItem("oauth_access_token_expires_at", expires_at);

      if (data.refresh_token) {
        localStorage.setItem("oauth_refresh_token", data.refresh_token);
      }

      return this.accessToken;
    } catch (error) {
      console.error("Token refresh error:", error);
      return false;
    }
  }

  /**
   * Handles OAuth callback with authorization code
   * @param urlParams URL search params containing authorization code
   * @returns Promise resolving to user data or null
   */
  public async handleOAuthCallback(
    urlParams: URLSearchParams,
  ): Promise<any | null> {
    const code = urlParams.get("code");
    const returnedState = urlParams.get("state");
    const error = urlParams.get("error");

    if (error) {
      throw new Error(`Authorization error: ${error}`);
    }

    if (code && returnedState) {
      // Verify state to prevent CSRF
      const storedState = localStorage.getItem("oauth_state");
      if (returnedState !== storedState) {
        throw new Error("State mismatch. Possible CSRF attack.");
      }

      // Exchange code for token
      return await this.generateToken(code);
    }

    return null;
  }

  /**
   * Logs user out by clearing tokens
   * @returns Success status
   */
  public logout(): boolean {
    this.accessToken = "";
    localStorage.removeItem("oauth_access_token");
    localStorage.removeItem("oauth_refresh_token");
    store.updateHasValidAccessToken(false);
    return true;
  }

  /**
   * Gets current access token
   * @returns Access token string
   */
  public async getAccessToken(): Promise<string> {
    if (!this.validateAccessTokenExpiresIn()) {
      const refreshToken = localStorage.getItem("oauth_refresh_token");
      if (refreshToken) {
        await this.refreshAccessToken(refreshToken);
      } else {
        return "";
      }
    }

    const accessToken =
      this.accessToken || localStorage.getItem("oauth_access_token") || "";

    return accessToken;
  }

  public validateAccessTokenExpiresIn(): boolean {
    const expiresAt = localStorage.getItem("oauth_access_token_expires_at");

    if (expiresAt === null) {
      return false;
    }

    if (this.currentEpochTime() > parseInt(expiresAt)) {
      return false;
    }

    return true;
  }

  currentEpochTime(): number {
    return Math.floor(new Date().getTime() / 1000);
  }

  public async listTools(): Promise<any> {
    const response = await fetch(this.config.mcpEndpoint, {
      method: "POST",
      headers: {
        accept: "application/json, text/event-stream",
        "Content-Type": "application/json",
        Authorization: `Bearer ${await this.getAccessToken()}`,
        "MCP-Protocol-Version": "2025-06-18",
      },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: "1",
        method: "tools/list",
        params: {
          additionalProp1: {},
        },
      }),
    });

    const result = response.json();

    return result;
  }

  public async callTool(tool: Tool) {
    console.log(`tool.inputJson: ${tool.inputJson}`);
    const response = await fetch(this.config.mcpEndpoint, {
      method: "POST",
      headers: {
        accept: "application/json, text/event-stream",
        "Content-Type": "application/json",
        Authorization: `Bearer ${await this.getAccessToken()}`,
        "MCP-Protocol-Version": "2025-06-18",
      },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: "1",
        method: "tools/call",
        params: {
          name: tool.name,
          arguments: JSON.parse(tool.inputJson),
        },
      }),
    });

    const result = response.json();

    return result;
  }

  public async *inference(
    messages: Array<Message>,
    tools: Array<Tool>,
  ): AsyncGenerator<string> {
    const response = await fetch(this.config.inferenceEndpoint, {
      method: "POST",
      headers: {
        accept: "text/event-stream, application/json",
        "Content-Type": "application/json",
        Authorization: `Bearer ${await this.getAccessToken()}`,
      },
      body: JSON.stringify({
        messages: messages,
        tools: tools,
      }),
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { value, done } = await reader.read();

      if (done) {
        break;
      }

      const chunkString = decoder.decode(value);
      console.log("chunkString ---");
      console.log(`${chunkString}`);

      for (const data of this.parseSSE(chunkString)) {
        yield data;
      }
    }
  }

  *parseSSE(chunk: string): any {
    const lines = chunk.split("\n");

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const jsonData = line.substring(6); // Remove 'data: ' prefix
          yield JSON.parse(jsonData);
        } catch (e) {
          // Skip invalid JSON lines
          continue;
        }
      }
    }
  }

  public convertMcpToolsForInference(mcpTools) {
    // Handle both direct tools array and nested result.tools structure
    const tools = mcpTools.result?.tools || mcpTools.tools || mcpTools;

    if (!Array.isArray(tools)) {
      console.warn("Expected tools to be an array, got:", typeof tools);
      return [];
    }

    return tools.map((tool) => {
      // Convert inputSchema to input_schema with proper structure
      const inputSchema = tool.inputSchema || {};

      // Build properties object from inputSchema
      const properties = {};
      const required = [];

      Object.entries(inputSchema).forEach(([key, value]) => {
        if (typeof value === "object" && value !== null) {
          // Map type from 'str' to 'string' and preserve other properties
          properties[key] = {
            type: value.type === "str" ? "string" : value.type,
            ...(value.description && { description: value.description }),
          };

          // If no required field is explicitly set, assume all fields are required
          // You might want to adjust this logic based on your specific needs
          required.push(key);
        }
      });

      return {
        name: tool.name,
        description: tool.description,
        input_schema: {
          type: "object",
          properties: properties,
          ...(required.length > 0 && { required: required }),
        },
      };
    });
  }
}
