import DataTable from "@/components/ui/DataTable";
import Badge from "@/components/ui/Badge";
import Link from "next/link";

interface Coupon {
  id: number;
  code: string;
  discount_type: string;
  discount_value: number;
}

async function getCoupons(): Promise<Coupon[]> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  try {
    const res = await fetch(`${base}/ecommerce/coupons`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export default async function CouponsPage() {
  const coupons = await getCoupons();

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Link href="/ecommerce" className="text-blue-600 hover:underline text-sm">← Products</Link>
          <h1 className="text-2xl font-bold text-gray-900">Coupons</h1>
        </div>
        <Link href="/ecommerce/coupons/new" className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700">
          + New Coupon
        </Link>
      </div>
      <div className="bg-white rounded-lg border border-gray-200">
        <DataTable
          columns={[
            {
              key: "code",
              header: "Code",
              render: (r) => (
                <span className="font-mono font-semibold text-purple-700">
                  {r.code as string}
                </span>
              ),
            },
            {
              key: "discount_type",
              header: "Discount Type",
              render: (r) => <Badge value={r.discount_type as string} />,
            },
            {
              key: "discount_value",
              header: "Discount Value",
              render: (r) => {
                const val = r.discount_value as number;
                const type = r.discount_type as string;
                return (
                  <span className="font-mono">
                    {type === "percentage" ? `${val}%` : `$${val.toFixed(2)}`}
                  </span>
                );
              },
            },
            {
              key: "actions",
              header: "Actions",
              render: (r) => (
                <Link href={`/ecommerce/coupons/${r.id}/edit`} className="text-blue-600 hover:underline text-xs">
                  Edit →
                </Link>
              ),
            },
          ]}
          rows={(coupons as unknown) as Record<string, unknown>[]}
          emptyMessage="No coupons found."
        />
      </div>
    </div>
  );
}
