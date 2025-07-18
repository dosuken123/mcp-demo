<script setup lang="ts">
import ToolSvg from "../svgs/Tool.vue";
import UserSvg from "../svgs/User.vue";

defineProps(["message"]);
</script>

<template>
  <!-- User messages (left side) -->
  <div class="flex items-start gap-2.5 justify-end">
    <template v-for="content in message.content">
      <template v-if="content.text">
        <div
          class="flex flex-col w-full leading-1.5 p-4 bg-gray-100 rounded-ss-xl rounded-b-xl"
        >
          <p class="text-sm font-normal text-gray-900">{{ content.text }}</p>
        </div>
        <user-svg />
      </template>
      <template v-else-if="content.tool_use_id">
        <tool-svg />
        <div
          class="flex flex-col w-full leading-1.5 p-4 bg-orange-100 rounded-t-xl rounded-b-xl"
        >
          <p class="text-xs font-semibold text-orange-800 mb-1">🔧 Tool Call</p>
          <p class="text-sm font-normal text-gray-900">{{ content.content }}</p>
        </div>
      </template>
    </template>
  </div>
</template>
