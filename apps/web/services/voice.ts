import { apiClient } from "@/lib/apiClient";
import type { VoiceToken } from "@/types";

export interface TokenRequest {
  room?: string;
  identity?: string;
  name?: string;
}

export const voiceApi = {
  /** Request a LiveKit join token so the browser can connect to a room. */
  token: (body: TokenRequest = {}) =>
    apiClient.post<VoiceToken>("/api/token", body),
};
