import StatCard from "@/components/ui/StatCard";

async function getStats() {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  try {
    const res = await fetch(`${base}/stats`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function DashboardPage() {
  const stats = await getStats();

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>
      {!stats && (
        <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800">
          Backend offline — start <code>uvicorn main:app --reload</code> in{" "}
          <code>APPS/odoo-frontend/backend/</code>
        </div>
      )}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <StatCard label="Total Users" value={stats?.users ?? "—"} href="/users" />
        <StatCard label="Active Memberships" value={stats?.active_memberships ?? "—"} />
        <StatCard label="Warehouses" value={stats?.warehouses ?? "—"} href="/wms" />
        <StatCard label="Open Pickings" value={stats?.open_pickings ?? "—"} href="/wms/pickings" />
        <StatCard label="Products" value={stats?.products ?? "—"} href="/ecommerce" />
        <StatCard label="Open Orders" value={stats?.open_orders ?? "—"} href="/ecommerce/orders" />
      </div>
    </div>
  );
}
