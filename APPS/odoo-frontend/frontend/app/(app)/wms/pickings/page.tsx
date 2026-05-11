import DataTable from "@/components/ui/DataTable";
import Badge from "@/components/ui/Badge";
import Link from "next/link";

interface Picking {
  id: number;
  state: string;
  picking_type_id: number;
}

async function getPickings(): Promise<Picking[]> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  try {
    const res = await fetch(`${base}/wms/pickings`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export default async function PickingsPage() {
  const pickings = await getPickings();

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Pickings</h1>
        <Link href="/wms/pickings/new" className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700">
          + New Picking
        </Link>
      </div>
      <div className="bg-white rounded-lg border border-gray-200">
        <DataTable
          columns={[
            { key: "id", header: "ID" },
            {
              key: "state",
              header: "State",
              render: (r) => <Badge value={r.state as string} />,
            },
            { key: "picking_type_id", header: "Type ID" },
            {
              key: "actions",
              header: "Actions",
              render: (r) => (
                <Link href={`/wms/pickings/${r.id}`} className="text-blue-600 hover:underline text-xs">
                  View →
                </Link>
              ),
            },
          ]}
          rows={(pickings as unknown) as Record<string, unknown>[]}
          emptyMessage="No pickings found."
        />
      </div>
    </div>
  );
}
