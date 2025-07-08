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
  <div class="bg-gray-100 h-screen flex flex-col max-w-lg mx-auto">
    <div class="bg-blue-500 p-4 text-white flex justify-between items-center">
      <button id="login" class="hover:bg-blue-400 rounded-md p-1">
        <svg width="25px" height="25px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <circle cx="12" cy="6" r="4" stroke="#ffffff" stroke-width="1.5"></circle> <path d="M15 20.6151C14.0907 20.8619 13.0736 21 12 21C8.13401 21 5 19.2091 5 17C5 14.7909 8.13401 13 12 13C15.866 13 19 14.7909 19 17C19 17.3453 18.9234 17.6804 18.7795 18" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"></path> </g></svg>
      </button>
      <span>Chat App</span>
      <div class="relative inline-block text-left">
      <button id="setting" class="hover:bg-blue-400 rounded-md p-1">
        <svg width="30px" height="30px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
          <g id="SVGRepo_iconCarrier"><path fill-rule="evenodd" clip-rule="evenodd" d="M14.1395 12.0002C14.1395 13.1048 13.2664 14.0002 12.1895 14.0002C11.1125 14.0002 10.2395 13.1048 10.2395 12.0002C10.2395 10.8957 11.1125 10.0002 12.1895 10.0002C13.2664 10.0002 14.1395 10.8957 14.1395 12.0002Z" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path> <path fill-rule="evenodd" clip-rule="evenodd" d="M7.57381 18.1003L5.12169 12.8133C4.79277 12.2907 4.79277 11.6189 5.12169 11.0963L7.55821 5.89229C7.93118 5.32445 8.55898 4.98876 9.22644 5.00029H12.1895H15.1525C15.8199 4.98876 16.4477 5.32445 16.8207 5.89229L19.2524 11.0923C19.5813 11.6149 19.5813 12.2867 19.2524 12.8093L16.8051 18.1003C16.4324 18.674 15.8002 19.0133 15.1281 19.0003H9.24984C8.5781 19.013 7.94636 18.6737 7.57381 18.1003Z" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path></g>
        </svg>
      </button>
      <div id="dropdown-content" class="hidden absolute right-0 mt-2 w-48 bg-white border border-gray-300 rounded-lg shadow-lg p-2">
        <a href="#" class="flex items-center px-4 py-2 text-gray-800 hover:bg-gray-200 rounded-md">
          <svg width="20px" height="20px" viewBox="0 0 24 24" fill="none" class="mr-2" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M9 21H12M15 21H12M12 21V18M12 18H19C20.1046 18 21 17.1046 21 16V7C21 5.89543 20.1046 5 19 5H5C3.89543 5 3 5.89543 3 7V16C3 17.1046 3.89543 18 5 18H12Z" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg>Appearance
        </a>
        <a href="#" class="flex items-center px-4 py-2 text-gray-800 hover:bg-gray-200 rounded-md">
          <svg width="20px" height="20px" viewBox="0 0 24 24" class="mr-2" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M11.2691 4.41115C11.5006 3.89177 11.6164 3.63208 11.7776 3.55211C11.9176 3.48263 12.082 3.48263 12.222 3.55211C12.3832 3.63208 12.499 3.89177 12.7305 4.41115L14.5745 8.54808C14.643 8.70162 14.6772 8.77839 14.7302 8.83718C14.777 8.8892 14.8343 8.93081 14.8982 8.95929C14.9705 8.99149 15.0541 9.00031 15.2213 9.01795L19.7256 9.49336C20.2911 9.55304 20.5738 9.58288 20.6997 9.71147C20.809 9.82316 20.8598 9.97956 20.837 10.1342C20.8108 10.3122 20.5996 10.5025 20.1772 10.8832L16.8125 13.9154C16.6877 14.0279 16.6252 14.0842 16.5857 14.1527C16.5507 14.2134 16.5288 14.2807 16.5215 14.3503C16.5132 14.429 16.5306 14.5112 16.5655 14.6757L17.5053 19.1064C17.6233 19.6627 17.6823 19.9408 17.5989 20.1002C17.5264 20.2388 17.3934 20.3354 17.2393 20.3615C17.0619 20.3915 16.8156 20.2495 16.323 19.9654L12.3995 17.7024C12.2539 17.6184 12.1811 17.5765 12.1037 17.56C12.0352 17.5455 11.9644 17.5455 11.8959 17.56C11.8185 17.5765 11.7457 17.6184 11.6001 17.7024L7.67662 19.9654C7.18404 20.2495 6.93775 20.3915 6.76034 20.3615C6.60623 20.3354 6.47319 20.2388 6.40075 20.1002C6.31736 19.9408 6.37635 19.6627 6.49434 19.1064L7.4341 14.6757C7.46898 14.5112 7.48642 14.429 7.47814 14.3503C7.47081 14.2807 7.44894 14.2134 7.41394 14.1527C7.37439 14.0842 7.31195 14.0279 7.18708 13.9154L3.82246 10.8832C3.40005 10.5025 3.18884 10.3122 3.16258 10.1342C3.13978 9.97956 3.19059 9.82316 3.29993 9.71147C3.42581 9.58288 3.70856 9.55304 4.27406 9.49336L8.77835 9.01795C8.94553 9.00031 9.02911 8.99149 9.10139 8.95929C9.16534 8.93081 9.2226 8.8892 9.26946 8.83718C9.32241 8.77839 9.35663 8.70162 9.42508 8.54808L11.2691 4.41115Z" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg>Favorite
        </a>
        <a href="#" class="flex items-center px-4 py-2 text-gray-800 hover:bg-gray-200 rounded-md">
          <svg width="20px" height="20px" viewBox="0 0 24 24" class="mr-2" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <g id="Warning / Info"> <path id="Vector" d="M12 11V16M12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12C21 16.9706 16.9706 21 12 21ZM12.0498 8V8.1L11.9502 8.1002V8H12.0498Z" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path> </g> </g></svg>More
        </a>
      </div>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto p-4">
      <div class="flex flex-col space-y-2">
        <ChatMesage v-for="message in messages" :message="message"/>
      </div>
    </div>
    
    <ChatForm @send-user-message="onSendUserMessage" />
  </div>
</template>
