"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(/access_token=([^;]+)/);
  return match ? match[1] : null;
}

const STATE_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-600",
  confirmed: "bg-blue-100 text-blue-700",
  processing: "bg-yellow-100 text-yellow-700",
  done: "bg-green-100 text-green-700",
  cancelled: "bg-red-100 text-red-600",
};

interface Order {
  id: number;
  reference: string;
  state: string;
  total_amount: number;
}

export default function MyOrdersPage() {
  const router = useRouter();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.replace("/store/login?next=/store/orders");
      return;
    }
    fetch(`${API_BASE}/store/orders`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then(setOrders)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return <div className="text-gray-400 py-8">Loading...</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-6">My Orders</h1>

      {orders.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-gray-400 mb-4">No orders yet.</p>
          <Link href="/store" className="text-indigo-600 hover:underline text-sm">
            Start shopping
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 divide-y divide-gray-100">
          {orders.map((o) => (
            <div key={o.id} className="flex items-center gap-4 p-4">
              <div className="flex-1">
                <p className="font-semibold text-gray-800">{o.reference}</p>
              </div>
              <span
                className={`text-xs font-medium px-2 py-1 rounded-full ${STATE_COLORS[o.state] ?? "bg-gray-100 text-gray-600"}`}
              >
                {o.state}
              </span>
              <p className="w-24 text-right font-semibold text-gray-800">
                ${o.total_amount.toFixed(2)}
              </p>
              <Link
                href={`/store/orders/${o.id}`}
                className="text-sm text-indigo-600 hover:underline"
              >
                View
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
