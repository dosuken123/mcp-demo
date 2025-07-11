<script setup lang="ts">
import { ref } from 'vue'
import { store } from './store'
import ChatMesage from './ChatMessage.vue'
import ChatForm from './ChatForm.vue'

const loading = ref(false)
const error = ref(null)
const messages = ref([]);

function convertMcpTools(mcpTools) {
  // Handle both direct tools array and nested result.tools structure
  const tools = mcpTools.result?.tools || mcpTools.tools || mcpTools;
  
  if (!Array.isArray(tools)) {
    console.warn('Expected tools to be an array, got:', typeof tools);
    return [];
  }

  return tools.map(tool => {
    // Convert inputSchema to input_schema with proper structure
    const inputSchema = tool.inputSchema || {};
    
    // Build properties object from inputSchema
    const properties = {};
    const required = [];
    
    Object.entries(inputSchema).forEach(([key, value]) => {
      if (typeof value === 'object' && value !== null) {
        // Map type from 'str' to 'string' and preserve other properties
        properties[key] = {
          type: value.type === 'str' ? 'string' : value.type,
          ...(value.description && { description: value.description })
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
        ...(required.length > 0 && { required: required })
      }
    };
  });
}

async function onSendUserMessage(content) {
  const message = { "content": content, "role": "user" }

  messages.value.push(message);

  const mcpClient = store.getMcpClient();
  const tools = convertMcpTools(store.mcpTools);
  for await (const response of mcpClient.inference(messages.value, tools)) {
    if (response?.delta?.text) {
        const lastMessage = messages.value[messages.value.length - 1];

        if (lastMessage.role === "user") {
          messages.value.push({ "content": response.delta.text, "role": "assistant" })
        }
        else if (lastMessage.role === "assistant") {
          lastMessage.content += response.delta.text
        }
        else {
          throw new Error(`Unsupported role ${lastMessage.role}`)
        }
    }
  };
}
</script>

<template>
  <div class="flex flex-col space-y-2">
    <ChatMesage v-for="message in messages" :message="message"/>
    <ChatForm @send-user-message="onSendUserMessage" />
  </div>
</template>
