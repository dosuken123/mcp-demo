<script setup lang="ts">
import { computed } from "vue";
import { marked } from "../../node_modules/marked";

const props = defineProps(["content", "role"]);

const compiledMarkdown = computed(() => {
  return marked.parse(props.content.text);
});
</script>

<template>
  <div
    v-if="role === 'assistant' && content.text"
    class="flex items-start gap-2.5 justify-end"
  >
    <div
      class="flex flex-col w-full leading-1.5 p-4 bg-blue-500 rounded-s-xl rounded-ee-xl"
    >
      <div
        class="text-sm font-normal text-white"
        v-html="compiledMarkdown"
      ></div>
    </div>
    <!-- Simple robot/AI assistant icon -->
    <svg
      width="25px"
      height="25px"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <!-- Robot head -->
      <rect
        x="7"
        y="8"
        width="10"
        height="8"
        rx="2"
        fill="#4f46e5"
        stroke="#3730a3"
        stroke-width="1"
      />

      <!-- Robot antenna -->
      <circle cx="12" cy="6" r="1" fill="#4f46e5" />
      <line x1="12" y1="7" x2="12" y2="8" stroke="#4f46e5" stroke-width="1" />

      <!-- Robot eyes -->
      <circle cx="10" cy="11" r="1" fill="#ffffff" />
      <circle cx="14" cy="11" r="1" fill="#ffffff" />

      <!-- Robot mouth -->
      <rect x="11" y="13" width="2" height="1" rx="0.5" fill="#ffffff" />
    </svg>
  </div>

  <!-- Tool call -->
  <div
    v-if="role === 'user' && content.tool_use_id"
    class="flex items-start gap-2.5 justify-start"
  >
    <svg
      width="25px"
      height="25px"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path d="M10 2L8 4L16 12L8 20L10 22L20 12L10 2Z" fill="#ea580c" />
    </svg>
    <div
      class="flex flex-col w-full leading-1.5 p-4 bg-orange-100 rounded-e-xl rounded-es-xl"
    >
      <p class="text-xs font-semibold text-orange-800 mb-1">🔧 Tool Call</p>
      <p class="text-sm font-normal text-gray-900">{{ content.content }}</p>
    </div>
  </div>

  <!-- User messages (left side) -->
  <div
    v-if="role === 'user' && content.text"
    class="flex items-start gap-2.5 justify-start"
  >
    <svg
      width="25px"
      height="25px"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
      <g
        id="SVGRepo_tracerCarrier"
        stroke-linecap="round"
        stroke-linejoin="round"
      ></g>
      <g id="SVGRepo_iconCarrier">
        <circle
          cx="12"
          cy="6"
          r="4"
          stroke="#ffffff"
          stroke-width="1.5"
        ></circle>
        <path
          d="M15 20.6151C14.0907 20.8619 13.0736 21 12 21C8.13401 21 5 19.2091 5 17C5 14.7909 8.13401 13 12 13C15.866 13 19 14.7909 19 17C19 17.3453 18.9234 17.6804 18.7795 18"
          stroke="#ffffff"
          stroke-width="1.5"
          stroke-linecap="round"
        ></path>
      </g>
    </svg>
    <div
      class="flex flex-col w-full leading-1.5 p-4 bg-gray-100 rounded-e-xl rounded-es-xl"
    >
      <p class="text-sm font-normal text-gray-900">{{ content.text }}</p>
    </div>
  </div>
</template>
