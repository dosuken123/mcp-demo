<script setup lang="ts">
import { ref } from 'vue'
import { store } from './store'
import ChatMesage from './ChatMessage.vue'
import ChatForm from './ChatForm.vue'
import { Message, MessageContent, Tool } from './MCPClient'

const loading = ref(false)
const error = ref(null)
const messages = ref<Message[]>([]);

async function processTextContentBlock(response) {
  if (response?.delta?.text) {
    const lastMessage = messages.value[messages.value.length - 1] as Message;

    if (lastMessage.role === "user") {
      const messageContent = { "type": "text", "text": response.delta.text } as MessageContent;
      const message = { "content": [messageContent], "role": "assistant" } as Message;
      messages.value.push(message)
    }
    else if (lastMessage.role === "assistant") {
      lastMessage.content[0].text += response.delta.text
    }
    else {
      throw new Error(`Unsupported role ${lastMessage.role}`)
    }
  }
}

async function processToolUseContentBlock(response, toolName, toolId) {
  const lastMessage = messages.value[messages.value.length - 1] as Message;
  const lastContent = lastMessage.content[lastMessage.content.length - 1] as MessageContent;

  if (lastContent.type != "tool_use") {
    lastMessage.content.push({ type: "tool_use", id: toolId, name: toolName, inputBuffer: "" } as MessageContent);
    return
  }

  if (response?.delta?.partial_json) {
    lastContent.inputBuffer += response.delta.partial_json;
  }
}

async function processInference() {
  let currentContentBlock = null;
  const mcpClient = store.getMcpClient();
  const tools = mcpClient.convertMcpToolsForInference(store.mcpTools);

  for await (const response of mcpClient.inference(messages.value, tools)) {
    if (response?.content_block) {
      currentContentBlock = response.content_block;
    }

    if (currentContentBlock?.type == "text") {
      processTextContentBlock(response);
    } else if (currentContentBlock?.type == "tool_use") {
      processToolUseContentBlock(response, currentContentBlock.name, currentContentBlock.id);
    }
  };
}

async function processTool() {
  const mcpClient = store.getMcpClient();
  const lastMessage = messages.value[messages.value.length - 1] as Message;
  const lastContent = lastMessage.content[lastMessage.content.length - 1] as MessageContent;  

  if (lastMessage.role == "assistant" && lastContent.type == "tool_use") {
    const result = await mcpClient.callTool({
      name: lastContent.name,
      id: lastContent.id,
      inputJson: lastContent.inputBuffer,
    })

    lastContent.input = JSON.parse(lastContent.inputBuffer);
    lastContent.inputBuffer = undefined;

    const toolResultContent = result?.result?.content?.[0]?.text;

    const messageContent = { "type": "tool_result", "tool_use_id": lastContent.id, "content": toolResultContent } as MessageContent;
    const message = { "content": [messageContent], "role": "user" } as Message;
    messages.value.push(message);

    await processInference();
  }
}

async function onSendUserMessage(content) {
  const messageContent = { "type": "text", "text": content } as MessageContent;
  const message = { "content": [messageContent], "role": "user" } as Message;
  messages.value.push(message);  
  
  await processInference();
  await processTool();
}
</script>

<template>
  <div class="flex flex-col space-y-2">
    <ChatMesage v-for="message in messages" :message="message"/>
    <ChatForm @send-user-message="onSendUserMessage" />
  </div>
</template>
