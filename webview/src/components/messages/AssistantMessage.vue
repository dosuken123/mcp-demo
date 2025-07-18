<script setup lang="ts">
import { marked } from "../../../node_modules/marked";
import AssistantSvg from "../svgs/Assistant.vue";

defineProps(["message"]);
</script>

<template>
  <div class="flex items-start gap-2.5 justify-start">
    <assistant-svg />
    <div
      class="flex flex-col w-full leading-1.5 p-4 bg-blue-500 rounded-se-xl rounded-b-xl"
    >
      <template v-for="content in message.content">
        <template v-if="content.text">
          <div
            class="text-sm font-normal text-white"
            v-html="marked.parse(content.text)"
          ></div>
        </template>
        <template v-else-if="content.id">
          <!-- Tool use -->
          <div
            class="p-4 mt-4 text-sm text-blue-800 rounded-lg bg-blue-50 dark:bg-gray-800 dark:text-blue-400"
            role="alert"
          >
            <span class="font-medium">method: {{ content.name }}</span>
            params: {{ content.input }}
          </div>
        </template>
      </template>
    </div>
  </div>
</template>
