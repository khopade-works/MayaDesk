import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: number | string;
  accent?: "default" | "danger" | "primary";
  loading?: boolean;
}

const accentClasses: Record<NonNullable<StatCardProps["accent"]>, string> = {
  default: "text-foreground",
  primary: "text-primary",
  danger: "text-danger",
};

export function StatCard({ label, value, accent = "default", loading }: StatCardProps) {
  return (
    <Card className="p-5">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className={cn("mt-2 text-3xl font-semibold tabular-nums", accentClasses[accent])}>
        {loading ? "—" : value}
      </p>
    </Card>
  );
}
