<script setup lang="ts">
import { ref } from 'vue'

const message = ref('');
const emit = defineEmits(['sendUserMessage'])

const submit = () => {
    emit('sendUserMessage', message.value);
    message.value = '';
}
</script>

<template>
    <div class="chat_form">
        <form @submit.prevent="submit">
            <textarea v-model="message" placeholder="enter your message"></textarea>
        </form>
        <button @click="submit">Send message</button>
    </div>
</template>
