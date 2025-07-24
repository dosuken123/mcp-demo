<script setup lang="ts">
import { ref, watch, useTemplateRef } from "vue";
import { store } from "./store";
import ChatMessage from "./ChatMessage.vue";
import ChatForm from "./ChatForm.vue";
import { Message, MessageContent, Tool } from "./MCPClient";

const loading = ref(false);
const error = ref(null);
const messages = ref<Message[]>([]);
const chatBoxBottom = ref(null);

watch(
  messages,
  async (newMessages, oldMessages) => {
    chatBoxBottom.value?.scrollIntoView({ behavior: "smooth" });
  },
  { deep: true, flush: "post" },
);

async function processInference() {
  const mcpClient = store.getMcpClient();
  const tools = mcpClient.convertMcpToolsForInference(store.mcpTools);

  for await (const response of mcpClient.inference(messages.value, tools)) {
    if (response?.type == "message_start") {
      messages.value.push({ content: [], role: "assistant" } as Message);
      continue;
    }

    const assistantMessage = messages.value[messages.value.length - 1];

    if (response?.type == "content_block_start") {
      if (response.content_block.type == "text") {
        const messageContent = { type: "text", text: "" } as MessageContent;
        assistantMessage.content.splice(response.index, 0, messageContent);
      } else if (response.content_block.type == "tool_use") {
        const messageContent = {
          type: "tool_use",
          id: response.content_block.id,
          name: response.content_block.name,
          inputBuffer: "",
        } as MessageContent;
        assistantMessage.content.splice(response.index, 0, messageContent);
      }
      continue;
    }

    if (response?.type == "content_block_delta") {
      const content = assistantMessage.content[response.index];

      if (content.type == "text") {
        content.text += response.delta.text;
      } else if (content.type == "tool_use") {
        content.inputBuffer += response.delta.partial_json;
      }
      continue;
    }

    if (response?.type == "content_block_stop") {
      const content = assistantMessage.content[response.index];

      if (content.type == "tool_use") {
        content.input = JSON.parse(content.inputBuffer);
        content.inputBuffer = undefined;
      }
      continue;
    }
  }
}

async function processTool(toolUseContent) {
  const mcpClient = store.getMcpClient();

  const result = await mcpClient.callTool({
    name: toolUseContent.name,
    id: toolUseContent.id,
    inputJson: JSON.stringify(toolUseContent.input),
  });

  const toolResultContent = result?.result?.content?.[0]?.text;

  const userMessage = messages.value[messages.value.length - 1];
  const content = userMessage.content.find(
    (content) => content.tool_use_id == toolUseContent.id,
  );
  content.content = toolResultContent;
}

async function processTools() {
  const assistantMessage = messages.value[messages.value.length - 1];

  if (assistantMessage.role !== "assistant") {
    console.warn("Not assistant message in processTools");
    return;
  }

  const toolUseContents = assistantMessage.content.filter(
    (content) => content.type == "tool_use",
  ) as Array<MessageContent>;

  if (toolUseContents.length === 0) {
    return;
  }

  // Prepare content result entries
  const toolResultContents = toolUseContents.map(
    (toolUseContent) =>
      ({
        type: "tool_result",
        tool_use_id: toolUseContent.id,
        content: "",
      }) as MessageContent,
  );

  const message = { content: toolResultContents, role: "user" } as Message;
  messages.value.push(message);

  const processes = toolUseContents.map((toolUseContent) =>
    processTool(toolUseContent),
  );

  await Promise.all(processes);
}

async function onSendUserMessage(content) {
  const messageContent = { type: "text", text: content } as MessageContent;
  const message = { content: [messageContent], role: "user" } as Message;
  messages.value.push(message);
  loading.value = true;

  while (true) {
    await processInference();
    await processTools();

    const lastMessage = messages.value[messages.value.length - 1];

    if (lastMessage.role === "assistant") {
      break;
    }
  }

  loading.value = false;
}
</script>

<template>
  <div class="flex flex-col space-y-2 h-85/100 overflow-y-auto">
    <chat-message v-for="message in messages" :message="message" />
    <div ref="chatBoxBottom"></div>
  </div>
  <div class="h-15/100">
    <chat-form :loading="loading" @send-user-message="onSendUserMessage" />
  </div>
  <div v-if="store.debug">{{ messages }}</div>
</template>
