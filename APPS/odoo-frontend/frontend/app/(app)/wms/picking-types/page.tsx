import DataTable from "@/components/ui/DataTable";
import Badge from "@/components/ui/Badge";
import Link from "next/link";

interface PickingType { id: number; name: string; operation_type: string; warehouse_id: number | null; active: boolean; }

async function getPickingTypes(): Promise<PickingType[]> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  try {
    const res = await fetch(`${base}/wms/picking-types`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
  } catch { return []; }
}

export default async function PickingTypesPage() {
  const types = await getPickingTypes();
  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Picking Types</h1>
        <Link href="/wms/picking-types/new" className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700">
          + New Picking Type
        </Link>
      </div>
      <div className="bg-white rounded-lg border border-gray-200">
        <DataTable
          columns={[
            { key: "id", header: "ID" },
            { key: "name", header: "Name" },
            { key: "operation_type", header: "Operation", render: (r) => <Badge value={r.operation_type as string} /> },
            { key: "warehouse_id", header: "Warehouse ID", render: (r) => <span className="text-gray-400">{(r.warehouse_id as number | null) ?? "—"}</span> },
            { key: "active", header: "Active", render: (r) => <span className={r.active ? "text-green-600" : "text-red-500"}>{r.active ? "✓" : "✗"}</span> },
          ]}
          rows={(types as unknown) as Record<string, unknown>[]}
          emptyMessage="No picking types."
        />
      </div>
    </div>
  );
}
