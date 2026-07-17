"use client";

import { AppointmentsTable } from "@/components/dashboard/AppointmentsTable";
import { CallbackQueue } from "@/components/dashboard/CallbackQueue";
import { EmergencyBanner } from "@/components/dashboard/EmergencyBanner";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { StatCard } from "@/components/dashboard/StatCard";
import { useDashboardStats } from "@/hooks/useDashboard";
import { useDashboardSocket } from "@/hooks/useDashboardSocket";

export default function DashboardPage() {
  useDashboardSocket();
  const { data: stats, isLoading } = useDashboardStats();

  return (
    <div className="flex min-h-screen">
      <Sidebar />

      <main className="flex-1 space-y-6 p-8">
        <header>
          <h1 className="text-2xl font-semibold">Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            Live clinic activity — updates automatically.
          </p>
        </header>

        <EmergencyBanner />

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Total appointments" value={stats?.appointments_total ?? 0} loading={isLoading} />
          <StatCard label="Upcoming" value={stats?.appointments_upcoming ?? 0} accent="primary" loading={isLoading} />
          <StatCard label="Pending callbacks" value={stats?.callbacks_pending ?? 0} loading={isLoading} />
          <StatCard label="Emergencies" value={stats?.emergencies_pending ?? 0} accent="danger" loading={isLoading} />
        </div>

        <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
          <AppointmentsTable />
          <CallbackQueue />
        </div>
      </main>
    </div>
  );
}
