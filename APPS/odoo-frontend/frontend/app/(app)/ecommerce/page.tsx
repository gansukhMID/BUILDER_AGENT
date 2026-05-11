import DataTable from "@/components/ui/DataTable";
import Link from "next/link";

interface ProductTemplate {
  id: number;
  name: string;
  list_price: number;
  variant_count: number;
}

async function getProducts(): Promise<ProductTemplate[]> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  try {
    const res = await fetch(`${base}/ecommerce/products`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export default async function EcommercePage() {
  const products = await getProducts();

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Products</h1>
        <div className="flex gap-3">
          <Link href="/ecommerce/orders" className="text-blue-600 hover:underline text-sm">Orders →</Link>
          <Link href="/ecommerce/coupons" className="text-blue-600 hover:underline text-sm">Coupons →</Link>
          <Link href="/ecommerce/products/new" className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700">
            + New Product
          </Link>
        </div>
      </div>
      <div className="bg-white rounded-lg border border-gray-200">
        <DataTable
          columns={[
            { key: "id", header: "ID" },
            { key: "name", header: "Name" },
            {
              key: "list_price",
              header: "List Price",
              render: (r) => (
                <span className="font-mono">${(r.list_price as number).toFixed(2)}</span>
              ),
            },
            {
              key: "variant_count",
              header: "Variants",
              render: (r) => (
                <span className="text-gray-600">{r.variant_count as number}</span>
              ),
            },
            {
              key: "actions",
              header: "Actions",
              render: (r) => (
                <Link
                  href={`/ecommerce/products/${r.id}/edit`}
                  className="text-blue-600 hover:underline text-xs"
                >
                  Edit →
                </Link>
              ),
            },
          ]}
          rows={(products as unknown) as Record<string, unknown>[]}
          emptyMessage="No products found."
        />
      </div>
    </div>
  );
}
