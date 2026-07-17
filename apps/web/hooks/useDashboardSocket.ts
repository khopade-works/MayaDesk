"use client";

import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * Subscribes to the dashboard WebSocket. On any event, invalidates the
 * dashboard queries so React Query refetches immediately. Reconnects with
 * backoff; polling (in the query hooks) is the fallback if the socket is down.
 */
export function useDashboardSocket() {
  const queryClient = useQueryClient();

  useEffect(() => {
    const wsUrl = `${API_URL.replace(/^http/, "ws")}/ws/dashboard`;
    let socket: WebSocket | null = null;
    let closedByUs = false;
    let retryTimer: ReturnType<typeof setTimeout> | undefined;

    const connect = () => {
      socket = new WebSocket(wsUrl);

      socket.onmessage = () => {
        queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      };
      socket.onclose = () => {
        if (!closedByUs) retryTimer = setTimeout(connect, 3000);
      };
      socket.onerror = () => {
        socket?.close();
      };
    };

    connect();

    return () => {
      closedByUs = true;
      if (retryTimer) clearTimeout(retryTimer);
      socket?.close();
    };
  }, [queryClient]);
}
