import DataTable from "@/components/ui/DataTable";

interface QuantDetail {
  product_name: string;
  location_name: string;
  lot_name: string | null;
  quantity: number;
}

async function getInventory(): Promise<QuantDetail[]> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  try {
    const res = await fetch(`${base}/wms/inventory`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export default async function InventoryPage() {
  const inventory = await getInventory();

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Inventory</h1>
      <div className="bg-white rounded-lg border border-gray-200">
        <DataTable
          columns={[
            { key: "product_name", header: "Product" },
            { key: "location_name", header: "Location" },
            { key: "lot_name", header: "Lot/Serial", render: (r) => (r.lot_name as string) ?? "—" },
            {
              key: "quantity",
              header: "Qty",
              render: (r) => (
                <span className="font-mono">{Number(r.quantity).toFixed(2)}</span>
              ),
            },
          ]}
          rows={(inventory as unknown) as Record<string, unknown>[]}
          emptyMessage="No inventory records. Run seed.py to populate."
        />
      </div>
    </div>
  );
}
