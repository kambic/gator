// composables/useChatWebSocket.ts
export function useChatWebSocket(roomId: string) {
  const messages = ref<Message[]>([])
  const connected = ref(false)
  const socket = new WebSocket(`wss://.../${roomId}`)

  socket.onmessage = (e) => {
    const data = JSON.parse(e.data)
    if (data.type === 'message') messages.value.push(data.payload)
  }

  // reconnect logic, ping/pong, etc.

  return { messages, send, connected }
}
