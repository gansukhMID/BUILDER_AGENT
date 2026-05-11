import Badge from "@/components/ui/Badge";
import DataTable from "@/components/ui/DataTable";
import Link from "next/link";

interface Profile {
  display_name: string | null;
  bio: string | null;
  phone: string | null;
  timezone: string | null;
  locale: string | null;
}

interface MembershipInfo {
  tier: string;
  started_at: string;
  expires_at: string | null;
}

interface UserDetail {
  id: number;
  email: string;
  is_active: boolean;
  profile: Profile | null;
  membership: MembershipInfo | null;
}

interface ActivityEvent {
  id: number;
  event_type: string;
  occurred_at: string;
  ip_address: string | null;
}

async function getUser(id: string): Promise<UserDetail | null> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  try {
    const res = await fetch(`${base}/users/${id}`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

async function getActivity(id: string): Promise<ActivityEvent[]> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  try {
    const res = await fetch(`${base}/users/${id}/activity`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default async function UserDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [user, activity] = await Promise.all([getUser(id), getActivity(id)]);

  if (!user) {
    return (
      <div>
        <Link href="/users" className="text-blue-600 hover:underline text-sm">
          ← Back to Users
        </Link>
        <p className="mt-4 text-gray-500">User not found.</p>
      </div>
    );
  }

  const recentActivity = activity.slice(0, 20);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Link href="/users" className="text-blue-600 hover:underline text-sm">
          ← Back to Users
        </Link>
        <Link
          href={`/users/${id}/edit`}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50"
        >
          Edit User
        </Link>
      </div>

      {/* User header */}
      <div className="flex items-center gap-4">
        <h1 className="text-2xl font-bold text-gray-900">{user.email}</h1>
        <Badge value={user.is_active ? "active" : "inactive"} />
      </div>

      {/* Profile card */}
      {user.profile && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-700 mb-4">Profile</h2>
          <dl className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <dt className="text-gray-500">Display Name</dt>
              <dd className="font-medium">{user.profile.display_name ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Phone</dt>
              <dd className="font-medium">{user.profile.phone ?? "—"}</dd>
            </div>
            <div className="col-span-2">
              <dt className="text-gray-500">Bio</dt>
              <dd className="font-medium">{user.profile.bio ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Timezone</dt>
              <dd className="font-medium">{user.profile.timezone ?? "UTC"}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Locale</dt>
              <dd className="font-medium">{user.profile.locale ?? "en"}</dd>
            </div>
          </dl>
        </div>
      )}

      {/* Membership card */}
      {user.membership && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-700 mb-4">Membership</h2>
          <div className="flex items-center gap-3 mb-4">
            <Badge value={user.membership.tier} />
          </div>
          <dl className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <dt className="text-gray-500">Started</dt>
              <dd className="font-medium">{formatDate(user.membership.started_at)}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Expires</dt>
              <dd className="font-medium">{formatDate(user.membership.expires_at)}</dd>
            </div>
          </dl>
        </div>
      )}

      {/* Activity log */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-4 py-3 border-b border-gray-100">
          <h2 className="font-semibold text-gray-700">
            Recent Activity ({recentActivity.length})
          </h2>
        </div>
        <DataTable
          columns={[
            {
              key: "event_type",
              header: "Event",
              render: (r) => (
                <span className="font-mono text-xs text-gray-700">{r.event_type as string}</span>
              ),
            },
            {
              key: "occurred_at",
              header: "Occurred At",
              render: (r) => (
                <span className="text-gray-500 text-sm">
                  {formatDate(r.occurred_at as string)}
                </span>
              ),
            },
            {
              key: "ip_address",
              header: "IP",
              render: (r) => (
                <span className="text-gray-400 text-xs font-mono">
                  {(r.ip_address as string | null) ?? "—"}
                </span>
              ),
            },
          ]}
          rows={(recentActivity as unknown) as Record<string, unknown>[]}
          emptyMessage="No activity recorded."
        />
      </div>
    </div>
  );
}
