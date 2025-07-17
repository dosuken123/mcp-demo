<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { store } from "./store";

onMounted(async () => {
  const mcpClient = store.getMcpClient();
  const tools = await mcpClient.listTools();
  store.updateMcpTools(tools);
});
</script>

<template>
  <div
    class="w-full bg-white border border-gray-200 rounded-lg shadow-sm dark:bg-gray-800 dark:border-gray-700"
  >
    <div class="sm:hidden">
      <label for="tabs" class="sr-only">Select tab</label>
      <select
        id="tabs"
        class="bg-gray-50 border-0 border-b border-gray-200 text-gray-900 text-sm rounded-t-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
      >
        <option>Tools</option>
      </select>
    </div>
    <ul
      class="hidden text-sm font-medium text-center text-gray-500 divide-x divide-gray-200 rounded-lg sm:flex dark:divide-gray-600 dark:text-gray-400 rtl:divide-x-reverse"
      id="fullWidthTab"
      data-tabs-toggle="#fullWidthTabContent"
      role="tablist"
    >
      <li class="w-full">
        <button
          id="tools-tab"
          data-tabs-target="#tools"
          type="button"
          role="tab"
          aria-controls="tools"
          aria-selected="true"
          class="inline-block w-full p-4 rounded-ss-lg bg-gray-50 hover:bg-gray-100 focus:outline-none dark:bg-gray-700 dark:hover:bg-gray-600"
        >
          Tools
        </button>
      </li>
    </ul>
    <div
      id="fullWidthTabContent"
      class="border-t border-gray-200 dark:border-gray-600"
    >
      <div
        class="hidden p-4 bg-white rounded-lg md:p-8 dark:bg-gray-800"
        id="tools"
        role="tabpanel"
        aria-labelledby="tools-tab"
      >
        <dl
          class="grid max-w-screen-xl grid-cols-1 gap-8 p-4 mx-auto text-gray-900 sm:grid-cols-1 xl:grid-cols-1 dark:text-white sm:p-8"
        >
          <div class="flex flex-col items-center justify-center">
            <dd class="text-gray-500 dark:text-gray-400">
              {{ store.mcpTools }}
            </dd>
          </div>
        </dl>
      </div>
    </div>
  </div>
</template>
