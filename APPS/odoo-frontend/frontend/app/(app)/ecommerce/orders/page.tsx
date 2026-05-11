import DataTable from "@/components/ui/DataTable";
import Badge from "@/components/ui/Badge";
import Link from "next/link";

interface Order {
  id: number;
  reference: string;
  state: string;
  total_amount: number;
  currency: string;
}

async function getOrders(): Promise<Order[]> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  try {
    const res = await fetch(`${base}/ecommerce/orders`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export default async function OrdersPage() {
  const orders = await getOrders();

  return (
    <div>
      <div className="flex items-center gap-4 mb-6">
        <Link href="/ecommerce" className="text-blue-600 hover:underline text-sm">
          ← Products
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Orders</h1>
      </div>
      <div className="bg-white rounded-lg border border-gray-200">
        <DataTable
          columns={[
            { key: "reference", header: "Reference" },
            {
              key: "state",
              header: "State",
              render: (r) => <Badge value={r.state as string} />,
            },
            {
              key: "total_amount",
              header: "Total",
              render: (r) => (
                <span className="font-mono">
                  {r.currency as string} {(r.total_amount as number).toFixed(2)}
                </span>
              ),
            },
            {
              key: "actions",
              header: "Actions",
              render: (r) => (
                <Link
                  href={`/ecommerce/orders/${r.id}`}
                  className="text-blue-600 hover:underline text-xs"
                >
                  View →
                </Link>
              ),
            },
          ]}
          rows={(orders as unknown) as Record<string, unknown>[]}
          emptyMessage="No orders found."
        />
      </div>
    </div>
  );
}
