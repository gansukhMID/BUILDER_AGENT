import Badge from "@/components/ui/Badge";
import DataTable from "@/components/ui/DataTable";
import Link from "next/link";

interface Move {
  id: number;
  product_id: number;
  product_qty: number;
  qty_done: number;
}

interface PickingDetail {
  id: number;
  state: string;
  moves: Move[];
}

async function getPicking(id: string): Promise<PickingDetail | null> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  try {
    const res = await fetch(`${base}/wms/pickings/${id}`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function PickingDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const picking = await getPicking(id);

  if (!picking) {
    return (
      <div>
        <Link href="/wms/pickings" className="text-blue-600 hover:underline text-sm">
          ← Back to Pickings
        </Link>
        <p className="mt-4 text-gray-500">Picking not found.</p>
      </div>
    );
  }

  return (
    <div>
      <Link href="/wms/pickings" className="text-blue-600 hover:underline text-sm">
        ← Back to Pickings
      </Link>
      <div className="mt-4 flex items-center gap-4 mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Picking #{picking.id}</h1>
        <Badge value={picking.state} />
      </div>
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-4 py-3 border-b border-gray-100">
          <h2 className="font-semibold text-gray-700">Moves ({picking.moves.length})</h2>
        </div>
        <DataTable
          columns={[
            { key: "id", header: "Move ID" },
            { key: "product_id", header: "Product ID" },
            { key: "product_qty", header: "Demand" },
            { key: "qty_done", header: "Done" },
          ]}
          rows={(picking.moves as unknown) as Record<string, unknown>[]}
          emptyMessage="No moves on this picking."
        />
      </div>
    </div>
  );
}
