// Types mirror the MayaDesk API response shapes (snake_case) so no mapping
// layer is needed between the backend DTOs and the UI.

export type AppointmentStatus =
  | "scheduled"
  | "confirmed"
  | "cancelled"
  | "completed"
  | "no_show";

export type CallbackPriority = "normal" | "urgent" | "emergency";

export type CallbackStatus = "pending" | "in_progress" | "resolved";

export interface AppointmentView {
  id: number;
  patient_name: string;
  patient_phone: string;
  provider_name: string;
  start_ts: string;
  end_ts: string;
  status: AppointmentStatus;
  reason?: string | null;
  created_at: string;
}

export interface CallbackView {
  id: number;
  patient_name?: string | null;
  patient_phone?: string | null;
  priority: CallbackPriority;
  reason: string;
  status: CallbackStatus;
  created_at: string;
}

export interface DashboardStats {
  appointments_total: number;
  appointments_upcoming: number;
  callbacks_pending: number;
  emergencies_pending: number;
}

export interface VoiceToken {
  token: string;
  url: string;
  room: string;
  identity: string;
}

export type ConnectionStatus =
  | "idle"
  | "connecting"
  | "connected"
  | "disconnected"
  | "error";
