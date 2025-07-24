<script setup lang="ts">
import { onMounted, ref } from "vue";
import Chat from "./components/Chat.vue";
import Tools from "./components/Tools.vue";
import { store } from "./components/store";

const isLoading = ref<boolean>(false);
const errorMessage = ref<string>("");
const successMessage = ref<string>("");

async function handleOAuthCallback() {
  try {
    // First check if we have an authorization code in the URL (callback from auth server)
    if (window.location.search.includes("code=")) {
      const urlParams = new URLSearchParams(window.location.search);
      const result = await store.getMcpClient().handleOAuthCallback(urlParams);

      if (result) {
        successMessage.value = "Authentication successful!";

        // Clean up URL after successful exchange
        const cleanUrl = window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
      }
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : String(error);
  } finally {
    isLoading.value = false;
  }
}

onMounted(async (): Promise<void> => {
  await handleOAuthCallback();

  store.updateHasValidAccessToken(
    !!(await store.getMcpClient().getAccessToken()),
  );
});

const logout = (): void => {
  store.getMcpClient().logout();
};

// Initiate OAuth flow with PKCE
const login = async (): Promise<void> => {
  try {
    isLoading.value = true;
    errorMessage.value = "";

    // Get authorization URL and redirect
    const authUrl = await store.getMcpClient().initiateOAuthFlow();
    window.location.href = authUrl;
  } catch (error) {
    console.error("OAuth initialization error:", error);
    errorMessage.value = error instanceof Error ? error.message : String(error);
  } finally {
    isLoading.value = false;
  }
};
</script>

<style>
@import "./components/style.css";
</style>

<template>
  <nav class="bg-white border-gray-200 dark:bg-gray-900 h-1/10">
    <div
      class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4 h-full"
    >
      <a
        href="https://flowbite.com/"
        class="flex items-center space-x-3 rtl:space-x-reverse"
      >
        <img
          src="https://flowbite.com/docs/images/logo.svg"
          class="h-8"
          alt="Flowbite Logo"
        />
        <span
          class="self-center text-2xl font-semibold whitespace-nowrap dark:text-white"
          >Chat</span
        >
      </a>
      <button
        data-collapse-toggle="navbar-default"
        type="button"
        class="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600"
        aria-controls="navbar-default"
        aria-expanded="false"
      >
        <span class="sr-only">Open main menu</span>
        <svg
          class="w-5 h-5"
          aria-hidden="true"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 17 14"
        >
          <path
            stroke="currentColor"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M1 1h15M1 7h15M1 13h15"
          />
        </svg>
      </button>
      <div class="hidden w-full md:block md:w-auto" id="navbar-default">
        <ul
          class="font-medium flex flex-col p-4 md:p-0 mt-4 border border-gray-100 rounded-lg bg-gray-50 md:flex-row md:space-x-8 rtl:space-x-reverse md:mt-0 md:border-0 md:bg-white dark:bg-gray-800 md:dark:bg-gray-900 dark:border-gray-700"
        >
          <li>
            <a
              href="#"
              class="block py-2 px-3 text-white bg-blue-700 rounded-sm md:bg-transparent md:text-blue-700 md:p-0 dark:text-white md:dark:text-blue-500"
              aria-current="page"
              >Home</a
            >
          </li>
          <template v-if="store.hasValidAccessToken">
            <li>
              <a
                href="#"
                @click="logout"
                class="block py-2 px-3 text-white bg-blue-700 rounded-sm md:bg-transparent md:text-blue-700 md:p-0 dark:text-white md:dark:text-blue-500"
                aria-current="page"
                >Logout</a
              >
            </li>
          </template>
          <template v-else>
            <li>
              <a
                href="#"
                @click="login"
                class="block py-2 px-3 text-white bg-blue-700 rounded-sm md:bg-transparent md:text-blue-700 md:p-0 dark:text-white md:dark:text-blue-500"
                aria-current="page"
                >Login</a
              >
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>

  <div class="p-4 sm:mx-64 h-9/10" v-if="store.hasValidAccessToken">
    <div class="mb-4 border-b border-gray-200 dark:border-gray-700 h-1/10">
      <ul
        class="flex flex-wrap -mb-px text-sm font-medium text-center"
        id="default-tab"
        data-tabs-toggle="#default-tab-content"
        role="tablist"
      >
        <li class="me-2" role="presentation">
          <button
            class="inline-block p-4 border-b-2 rounded-t-lg"
            id="chat-tab"
            data-tabs-target="#chat"
            type="button"
            role="tab"
            aria-controls="chat"
            aria-selected="false"
          >
            Chat
          </button>
        </li>
        <li class="me-2" role="presentation">
          <button
            class="inline-block p-4 border-b-2 rounded-t-lg hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300"
            id="tool-tab"
            data-tabs-target="#tool"
            type="button"
            role="tab"
            aria-controls="tool"
            aria-selected="false"
          >
            Tools
          </button>
        </li>
      </ul>
    </div>
    <div id="default-tab-content" class="h-9/10">
      <div
        class="hidden p-4 rounded-lg bg-gray-50 dark:bg-gray-800 h-full"
        id="chat"
        role="tabpanel"
        aria-labelledby="chat-tab"
      >
        <chat />
      </div>
      <div
        class="hidden p-4 rounded-lg bg-gray-50 dark:bg-gray-800"
        id="tool"
        role="tabpanel"
        aria-labelledby="tool-tab"
      >
        <tools />
      </div>
    </div>
  </div>
</template>
