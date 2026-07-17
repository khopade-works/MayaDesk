import { cn } from "@/lib/utils";

const navItems = ["Overview", "Appointments", "Callbacks", "Settings"] as const;

/**
 * Placeholder staff dashboard sidebar. Routing, active-link state, and
 * auth-aware nav items are wired up in Phase 6.
 */
export function Sidebar() {
  return (
    <aside className="hidden w-56 shrink-0 border-r border-border bg-card px-4 py-6 sm:block">
      <p className="mb-6 px-2 text-lg font-semibold">MayaDesk</p>
      <nav className="flex flex-col gap-1">
        {navItems.map((item, index) => (
          <span
            key={item}
            className={cn(
              "rounded-md px-2 py-2 text-sm text-muted-foreground",
              index === 0 && "bg-muted text-foreground"
            )}
          >
            {item}
          </span>
        ))}
      </nav>
    </aside>
  );
}
