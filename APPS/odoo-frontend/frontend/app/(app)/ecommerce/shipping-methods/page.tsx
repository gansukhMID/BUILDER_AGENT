import DataTable from "@/components/ui/DataTable";
import Link from "next/link";

interface ShippingRow { id: number; name: string; carrier: string | null; price: number; active: boolean; }

async function getMethods(): Promise<ShippingRow[]> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  try {
    const res = await fetch(`${base}/ecommerce/shipping-methods`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
  } catch { return []; }
}

export default async function ShippingMethodsPage() {
  const methods = await getMethods();
  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Shipping Methods</h1>
        <Link href="/ecommerce/shipping-methods/new"
          className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700">
          + New Method
        </Link>
      </div>
      <div className="bg-white rounded-lg border border-gray-200">
        <DataTable
          columns={[
            { key: "id", header: "ID" },
            { key: "name", header: "Name" },
            { key: "carrier", header: "Carrier", render: (r) => <span className="text-gray-500">{(r.carrier as string | null) ?? "—"}</span> },
            { key: "price", header: "Price", render: (r) => <span>${(r.price as number).toFixed(2)}</span> },
            { key: "active", header: "Active", render: (r) => <span className={r.active ? "text-green-600" : "text-red-500"}>{r.active ? "✓" : "✗"}</span> },
          ]}
          rows={(methods as unknown) as Record<string, unknown>[]}
          emptyMessage="No shipping methods."
        />
      </div>
    </div>
  );
}
