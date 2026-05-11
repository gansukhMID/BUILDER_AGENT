import Badge from "@/components/ui/Badge";
import DataTable from "@/components/ui/DataTable";
import Link from "next/link";

interface OrderLine {
  id: number;
  quantity: number;
  unit_price: number;
  line_total: number;
}

interface OrderDetail {
  id: number;
  reference: string;
  state: string;
  total_amount: number;
  lines: OrderLine[];
}

async function getOrder(id: string): Promise<OrderDetail | null> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  try {
    const res = await fetch(`${base}/ecommerce/orders/${id}`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function OrderDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const order = await getOrder(id);

  if (!order) {
    return (
      <div>
        <Link href="/ecommerce/orders" className="text-blue-600 hover:underline text-sm">
          ← Back to Orders
        </Link>
        <p className="mt-4 text-gray-500">Order not found.</p>
      </div>
    );
  }

  return (
    <div>
      <Link href="/ecommerce/orders" className="text-blue-600 hover:underline text-sm">
        ← Back to Orders
      </Link>
      <div className="mt-4 flex items-center gap-4 mb-2">
        <h1 className="text-2xl font-bold text-gray-900">{order.reference}</h1>
        <Badge value={order.state} />
      </div>
      <p className="text-gray-600 mb-6 font-mono text-lg">
        Total: ${order.total_amount.toFixed(2)}
      </p>
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-4 py-3 border-b border-gray-100">
          <h2 className="font-semibold text-gray-700">Lines ({order.lines.length})</h2>
        </div>
        <DataTable
          columns={[
            { key: "id", header: "Line ID" },
            {
              key: "quantity",
              header: "Qty",
              render: (r) => <span>{r.quantity as number}</span>,
            },
            {
              key: "unit_price",
              header: "Unit Price",
              render: (r) => (
                <span className="font-mono">${(r.unit_price as number).toFixed(2)}</span>
              ),
            },
            {
              key: "line_total",
              header: "Line Total",
              render: (r) => (
                <span className="font-mono font-semibold">
                  ${(r.line_total as number).toFixed(2)}
                </span>
              ),
            },
          ]}
          rows={(order.lines as unknown) as Record<string, unknown>[]}
          emptyMessage="No lines on this order."
        />
      </div>
    </div>
  );
}
