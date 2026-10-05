import { AppShell } from "@/components/AppShell";
import { LoadingState } from "@/components/LoadingState";

export default function Loading() {
  return (
    <AppShell>
      <div className="page loading-page">
        <LoadingState label="Opening analysis" detail="Loading the persisted landscape and evidence state." />
      </div>
    </AppShell>
  );
}
