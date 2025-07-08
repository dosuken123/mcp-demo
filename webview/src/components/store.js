import { reactive } from 'vue'
import MCPClient from './MCPClient'

export const store = reactive({
    mcpClinet: null,
    mcpTools: [],
    hasValidAccessToken: false,

    updateHasValidAccessToken(flag) {
        this.hasValidAccessToken = flag
    },
    updateMcpTools(tools) {
        this.mcpTools = tools;
    },
    getMcpClient() {
        if (this.mcpClinet) { return this.mcpClinet }

        // Initialize MCP client
        this.mcpClinet = new MCPClient({
        // You can override default config here if needed
        // authorizationEndpoint: 'http://custom-domain/oauth/authorize',
        })

        return this.mcpClinet
    }
})
