<script lang="ts" setup>
import { ref, onMounted, onUpdated } from 'vue';
import ServiceHTTP from '../../../api/service'


// State of chatBot
const messages = ref<{ role: string; content: string }[]>([]);
const userInput = ref('');
const messagesContainer = ref<HTMLDivElement | null>(null);
const isLoading = ref(false);

onMounted(() => {
  const savedMessages = localStorage.getItem('chatbot-messages');
  if (savedMessages) {
    messages.value = JSON.parse(savedMessages);
  }
});


// Send message to chatBot
async function sendMessage() {
  const user_input = userInput.value.trim();
  if (!user_input) return;

  // Aggiungi il messaggio dell'utente
  const message = messages.value.push({ role: 'user', content: userInput.value });
  localStorage.setItem('user',JSON.stringify(message))
  localStorage.setItem('chatbot-messages', JSON.stringify(messages.value));

  userInput.value = '';
  isLoading.value = true;

  try {
    const response = await ServiceHTTP.userQuery(user_input)
    const bot_response = response.text

    // Check if text response is empty
    if(!bot_response){
      messages.value.push({ role: 'bot', content: 'Unable to display bot response, feature not available yet' });
      localStorage.setItem('chatbot-messages', JSON.stringify(messages.value));
      return;
    }

    // Add the bot response
    messages.value.push({ role: 'bot', content: bot_response });
    localStorage.setItem('chatbot-messages', JSON.stringify(messages.value));
    

  }
  catch (error) {
    console.error('Error fetching chatBot response:', error)
    messages.value.push({ role: 'bot', content: 'Error in response' });
    localStorage.setItem('chatbot-messages', JSON.stringify(messages.value));
  }
  finally {
    isLoading.value = false;
  }
};

// Scroll to bottom when new message is added
onUpdated(() => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
});
// Clear chat
const clearChat = () => {
  messages.value = [];
  localStorage.removeItem('chatbot-messages');
};
</script>

<template>
  <h1 class="page-title font-bold">Chatbot</h1>
    <VaButton class="w-fit h-fit mb-5" preset="primary" @click="clearChat">
      Clear chat
    </VaButton>

  <!-- Contenitore dei messaggi -->
  <section ref="messagesContainer" class="flex flex-col gap-4 messages-container">
    <div class="messages">
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="message.role === 'user' ? 'user-message' : 'bot-message'"
        class="message"
      >
        {{ message.content }}
      </div>
    </div>

    <!-- Spinner di caricamento -->
    <div v-if="isLoading" class="flex justify-center items-center mt-4">
      <VaProgressCircle indeterminate size="medium" />
      <span class="ml-2">Loading...</span>
    </div>
  </section>

  <!-- Input e bottone -->
  <div class="input-container flex gap-2">
    <input
      v-model="userInput"
      type="text"
      placeholder="Ask me anything..."
      class="input"
      @keyup.enter="sendMessage"
    />
    <button @click="sendMessage" class="button" :disabled="isLoading">Send</button>
  </div>
</template>

<style scoped>
/* Contenitore messaggi */
.messages-container {
  max-height: calc(100vh - 200px); /* Altezza dinamica basata sulla viewport */
  overflow-y: auto;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  margin-bottom: 10px;
  display: flex;
  flex-direction: column;
  background-color: #ebebeb;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.message {
  max-width: 60%;
  padding: 10px;
  border-radius: 5px;
  /*font-size: 1.2rem; */
  word-wrap: break-word; /* Avvolge le parole lunghe */
  word-break: break-word; /* Forza l'interruzione delle parole lunghe */
  overflow-wrap: break-word; /* Garantisce l'interruzione in browser moderni */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); /* Aggiunge un'ombra leggera */
}

.user-message {
  align-self: flex-end;
  background-color: #c4d8f7;
  text-align: right;
}

.bot-message {
  align-self: flex-start;
  background-color: #f0f0f0;
  text-align: left;
}

/* Stile input */
.input-container {
  position: sticky;
  bottom: 0;
  padding: 10px 0;
}

.input-container .input {
  flex: 1;
  padding: 15px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.input-container .button {
  padding: 15px 20px;
  background-color: #154ec1;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.input-container .button:hover {
  background-color: #45a049;
}

.reset-button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background-color: #f44336;
}

.reset-button:hover {
  background-color: #e53935;
}
</style>

