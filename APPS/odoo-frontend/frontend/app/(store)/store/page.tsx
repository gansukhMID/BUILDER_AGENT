import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface Product {
  id: number;
  name: string;
  list_price: number;
  variant_count: number;
}

async function getProducts(): Promise<Product[]> {
  const res = await fetch(`${API_BASE}/store/products`, { cache: "no-store" });
  if (!res.ok) return [];
  return res.json();
}

export default async function StorePage() {
  const products = await getProducts();

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Products</h1>
      {products.length === 0 ? (
        <p className="text-gray-500">No products available.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((p) => (
            <div
              key={p.id}
              className="bg-white rounded-lg border border-gray-200 p-5 flex flex-col gap-3 hover:shadow-md transition-shadow"
            >
              <div>
                <h2 className="text-lg font-semibold text-gray-800">{p.name}</h2>
                <p className="text-sm text-gray-500 mt-1">
                  {p.variant_count} variant{p.variant_count !== 1 ? "s" : ""}
                </p>
              </div>
              <p className="text-xl font-bold text-indigo-600">
                ${p.list_price.toFixed(2)}
              </p>
              <Link
                href={`/store/products/${p.id}`}
                className="mt-auto text-center bg-indigo-600 text-white text-sm rounded px-4 py-2 hover:bg-indigo-700"
              >
                View Product
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
