import DataTable from "@/components/ui/DataTable";
import Link from "next/link";

interface CategoryRow { id: number; name: string; parent_id: number | null; }

async function getCategories(): Promise<CategoryRow[]> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  try {
    const res = await fetch(`${base}/ecommerce/categories`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
  } catch { return []; }
}

export default async function CategoriesPage() {
  const categories = await getCategories();
  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Product Categories</h1>
        <Link href="/ecommerce/categories/new"
          className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700">
          + New Category
        </Link>
      </div>
      <div className="bg-white rounded-lg border border-gray-200">
        <DataTable
          columns={[
            { key: "id", header: "ID" },
            { key: "name", header: "Name" },
            { key: "parent_id", header: "Parent ID", render: (r) => <span className="text-gray-400">{(r.parent_id as number | null) ?? "—"}</span> },
          ]}
          rows={(categories as unknown) as Record<string, unknown>[]}
          emptyMessage="No categories."
        />
      </div>
    </div>
  );
}
