"use client";

import { useState } from "react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { useAppointments } from "@/hooks/useDashboard";
import { formatDateTime } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { AppointmentStatus } from "@/types";

const STATUS_FILTERS: Array<{ label: string; value: AppointmentStatus | "all" }> = [
  { label: "All", value: "all" },
  { label: "Scheduled", value: "scheduled" },
  { label: "Confirmed", value: "confirmed" },
  { label: "Completed", value: "completed" },
  { label: "Cancelled", value: "cancelled" },
];

const statusBadge: Record<AppointmentStatus, string> = {
  scheduled: "bg-primary/15 text-primary",
  confirmed: "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400",
  completed: "bg-muted text-muted-foreground",
  cancelled: "bg-danger/15 text-danger",
  no_show: "bg-amber-500/15 text-amber-600 dark:text-amber-400",
};

export function AppointmentsTable() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<AppointmentStatus | "all">("all");

  const { data: appointments = [], isLoading } = useAppointments({
    search: search.trim() || undefined,
    status: status === "all" ? undefined : status,
  });

  return (
    <Card>
      <CardHeader className="gap-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <CardTitle>Appointments</CardTitle>
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name or phone…"
            className="h-9 w-64 max-w-full rounded-md border border-border bg-background px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          {STATUS_FILTERS.map((f) => (
            <button
              key={f.value}
              onClick={() => setStatus(f.value)}
              className={cn(
                "rounded-full px-3 py-1 text-xs font-medium transition-colors",
                status === f.value
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground hover:bg-muted/70"
              )}
            >
              {f.label}
            </button>
          ))}
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-xs uppercase text-muted-foreground">
              <tr className="border-b border-border">
                <th className="py-2 pr-4 font-medium">Patient</th>
                <th className="py-2 pr-4 font-medium">Provider</th>
                <th className="py-2 pr-4 font-medium">When</th>
                <th className="py-2 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {isLoading && (
                <tr>
                  <td colSpan={4} className="py-6 text-center text-muted-foreground">
                    Loading…
                  </td>
                </tr>
              )}
              {!isLoading && appointments.length === 0 && (
                <tr>
                  <td colSpan={4} className="py-6 text-center text-muted-foreground">
                    No appointments found.
                  </td>
                </tr>
              )}
              {appointments.map((a) => (
                <tr key={a.id} className="border-b border-border/60 last:border-0">
                  <td className="py-3 pr-4">
                    <div className="font-medium">{a.patient_name}</div>
                    <div className="text-xs text-muted-foreground">{a.patient_phone}</div>
                  </td>
                  <td className="py-3 pr-4">{a.provider_name}</td>
                  <td className="py-3 pr-4 whitespace-nowrap">{formatDateTime(a.start_ts)}</td>
                  <td className="py-3">
                    <span
                      className={cn(
                        "rounded-full px-2 py-0.5 text-xs font-medium capitalize",
                        statusBadge[a.status]
                      )}
                    >
                      {a.status.replace("_", " ")}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
