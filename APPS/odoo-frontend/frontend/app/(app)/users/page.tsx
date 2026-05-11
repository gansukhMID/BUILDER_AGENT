import DataTable from "@/components/ui/DataTable";
import Link from "next/link";

interface UserRow {
  id: number;
  email: string;
  is_active: boolean;
  last_login_at: string | null;
}

async function getUsers(): Promise<UserRow[]> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  try {
    const res = await fetch(`${base}/users`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

function formatDate(iso: string | null): string {
  if (!iso) return "Never";
  return new Date(iso).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export default async function UsersPage() {
  const users = await getUsers();

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Users</h1>
      <div className="bg-white rounded-lg border border-gray-200">
        <DataTable
          columns={[
            { key: "id", header: "ID" },
            { key: "email", header: "Email" },
            {
              key: "is_active",
              header: "Active",
              render: (r) => (
                <span className={r.is_active ? "text-green-600 font-bold" : "text-red-500"}>
                  {r.is_active ? "✓" : "✗"}
                </span>
              ),
            },
            {
              key: "last_login_at",
              header: "Last Login",
              render: (r) => (
                <span className="text-gray-500 text-sm">
                  {formatDate(r.last_login_at as string | null)}
                </span>
              ),
            },
            {
              key: "actions",
              header: "Actions",
              render: (r) => (
                <Link
                  href={`/users/${r.id}`}
                  className="text-blue-600 hover:underline text-xs"
                >
                  View →
                </Link>
              ),
            },
          ]}
          rows={(users as unknown) as Record<string, unknown>[]}
          emptyMessage="No users found."
        />
      </div>
    </div>
  );
}
