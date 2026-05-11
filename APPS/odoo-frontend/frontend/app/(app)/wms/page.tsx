import DataTable from "@/components/ui/DataTable";

interface Warehouse {
  id: number;
  name: string;
  code: string | null;
}

async function getWarehouses(): Promise<Warehouse[]> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  try {
    const res = await fetch(`${base}/wms/warehouses`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export default async function WMSPage() {
  const warehouses = await getWarehouses();

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Warehouses</h1>
      <div className="bg-white rounded-lg border border-gray-200">
        <DataTable
          columns={[
            { key: "id", header: "ID" },
            { key: "name", header: "Name" },
            { key: "code", header: "Code", render: (r) => (r.code as string) ?? "—" },
          ]}
          rows={(warehouses as unknown) as Record<string, unknown>[]}
          emptyMessage="No warehouses found. Run the seed script to add data."
        />
      </div>
    </div>
  );
}
