import { useState, useEffect, useCallback, useRef } from 'react';

// Use Vite dev server which proxies to backend
const WS_URL = 'ws://localhost:5173/ws';

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [lastMessage, setLastMessage] = useState(null);
  const wsRef = useRef(null);
  const clientIdRef = useRef(null);

  const connect = useCallback(() => {
    // Gera um ID único para o cliente
    if (!clientIdRef.current) {
      clientIdRef.current = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // Se já existe conexão, não cria outra
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const ws = new WebSocket(`${WS_URL}/${clientIdRef.current}`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket conectado');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastMessage(data);
        setMessages((prev) => [...prev, data]);
      } catch (error) {
        console.error('Erro ao parsear mensagem:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('Erro no WebSocket:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket desconectado');
      setIsConnected(false);
      
      // Tenta reconectar após 3 segundos
      setTimeout(() => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
          connect();
        }
      }, 3000);
    };
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const sendMessage = useCallback((message) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  // Conexão automática ao montar o componente
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    messages,
    lastMessage,
    sendMessage,
    connect,
    disconnect
  };
}

export default useWebSocket;
