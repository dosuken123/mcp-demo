<script setup lang="ts">
import { ref, computed } from "vue";

const props = defineProps(["loading"]);

const message = ref("");
const emit = defineEmits(["sendUserMessage"]);

const submit = () => {
  emit("sendUserMessage", message.value);
  message.value = "";
};

const placeholder = computed(() => {
  return props.loading ? "Working on it..." : "Ask me anything!";
});
</script>

<template>
  <label for="chat" class="sr-only">Your message</label>
  <div
    class="flex items-center content-center px-3 py-2 rounded-lg bg-gray-50 dark:bg-gray-700 h-full"
  >
    <textarea
      v-model="message"
      v-on:keyup.enter="submit"
      id="chat"
      rows="1"
      class="block mx-4 w-full h-full text-sm text-gray-900 bg-white rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
      :placeholder="placeholder"
      :disabled="loading === true"
    ></textarea>
    <button
      type="submit"
      @click="submit"
      class="inline-flex justify-center p-2 text-blue-600 rounded-full cursor-pointer dark:text-blue-500"
      :disabled="loading === true"
      :class="{
        'hover:bg-blue-100 dark:hover:bg-gray-600': !loading,
        'cursor-not-allowed bg-gray-300 opacity-50': loading,
      }"
    >
      <svg
        class="w-5 h-5 rotate-90 rtl:-rotate-90"
        aria-hidden="true"
        xmlns="http://www.w3.org/2000/svg"
        fill="currentColor"
        viewBox="0 0 18 20"
      >
        <path
          d="m17.914 18.594-8-18a1 1 0 0 0-1.828 0l-8 18a1 1 0 0 0 1.157 1.376L8 18.281V9a1 1 0 0 1 2 0v9.281l6.758 1.689a1 1 0 0 0 1.156-1.376Z"
        />
      </svg>
      <span class="sr-only">Send message</span>
    </button>
  </div>
</template>
