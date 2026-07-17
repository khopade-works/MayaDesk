"use client";

import { useQuery } from "@tanstack/react-query";

import { dashboardApi, type AppointmentQuery } from "@/services/dashboard";

// Polling interval for near-real-time updates. Reads the shared DB, so it
// reflects writes from both the API and the voice agent process.
const POLL_MS = 5000;

export function useDashboardStats() {
  return useQuery({
    queryKey: ["dashboard", "stats"],
    queryFn: dashboardApi.stats,
    refetchInterval: POLL_MS,
  });
}

export function useAppointments(query: AppointmentQuery = {}) {
  return useQuery({
    queryKey: ["dashboard", "appointments", query],
    queryFn: () => dashboardApi.appointments(query),
    refetchInterval: POLL_MS,
  });
}

export function useCallbacks() {
  return useQuery({
    queryKey: ["dashboard", "callbacks"],
    queryFn: () => dashboardApi.callbacks(),
    refetchInterval: POLL_MS,
  });
}

export function useEmergencies() {
  return useQuery({
    queryKey: ["dashboard", "emergencies"],
    queryFn: dashboardApi.emergencies,
    refetchInterval: POLL_MS,
  });
}
