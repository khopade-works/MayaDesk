import { apiClient } from "@/lib/apiClient";
import type {
  AppointmentStatus,
  AppointmentView,
  CallbackStatus,
  CallbackView,
  DashboardStats,
} from "@/types";

export interface AppointmentQuery {
  status?: AppointmentStatus;
  search?: string;
}

function toQueryString(params: Record<string, string | undefined>): string {
  const usp = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value) usp.set(key, value);
  }
  const qs = usp.toString();
  return qs ? `?${qs}` : "";
}

export const dashboardApi = {
  stats: () => apiClient.get<DashboardStats>("/api/dashboard/stats"),

  appointments: (query: AppointmentQuery = {}) =>
    apiClient.get<AppointmentView[]>(
      `/api/dashboard/appointments${toQueryString({
        status: query.status,
        search: query.search,
      })}`
    ),

  callbacks: (status?: CallbackStatus) =>
    apiClient.get<CallbackView[]>(
      `/api/dashboard/callbacks${toQueryString({ status })}`
    ),

  emergencies: () => apiClient.get<CallbackView[]>("/api/dashboard/emergencies"),
};
