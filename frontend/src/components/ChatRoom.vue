<!-- ChatRoom.vue -->
<script setup>
import { useChatWebSocket } from '@/composables/useChatWebSocket'
import { useTypingIndicator } from '@/composables/useTypingIndicator'

const route = useRoute()
const { messages, send, connected } = useChatWebSocket(route.params.id)
const { typingUsers } = useTypingIndicator(messages)
</script>

<template>
  <div class="chat-room">
    <MessageList :messages="messages" />
    <div v-if="typingUsers.length" class="typing">
      {{ typingUsers.join(', ') }} is typing...
    </div>
<!--    <ChatInput @send="send" />-->
  </div>
</template>
