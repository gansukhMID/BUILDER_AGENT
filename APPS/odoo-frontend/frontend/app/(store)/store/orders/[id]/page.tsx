"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
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

interface OrderLine {
  id: number;
  variant_id: number | null;
  qty: number;
  unit_price: number;
  subtotal: number;
}

interface OrderDetail {
  id: number;
  reference: string;
  state: string;
  total_amount: number;
  coupon_discount: number;
  lines: OrderLine[];
}

export default function OrderDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [order, setOrder] = useState<OrderDetail | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.replace(`/store/login?next=/store/orders/${id}`);
      return;
    }
    fetch(`${API_BASE}/store/orders/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => {
        if (r.status === 403) throw new Error("Not authorized to view this order");
        if (r.status === 404) throw new Error("Order not found");
        if (!r.ok) throw new Error("Failed to load order");
        return r.json();
      })
      .then(setOrder)
      .catch((e: Error) => setError(e.message));
  }, [id, router]);

  if (error) {
    return (
      <div className="text-center py-16">
        <p className="text-red-500 mb-4">{error}</p>
        <Link href="/store/orders" className="text-indigo-600 hover:underline text-sm">
          Back to orders
        </Link>
      </div>
    );
  }

  if (!order) return <div className="text-gray-400 py-8">Loading...</div>;

  return (
    <div className="max-w-xl mx-auto">
      <nav className="text-sm text-gray-500 mb-6">
        <Link href="/store/orders" className="hover:text-indigo-600">Orders</Link>
        <span className="mx-2">›</span>
        <span className="text-gray-800">{order.reference}</span>
      </nav>

      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-bold text-gray-800">{order.reference}</h1>
          <span
            className={`text-xs font-medium px-2 py-1 rounded-full ${STATE_COLORS[order.state] ?? "bg-gray-100 text-gray-600"}`}
          >
            {order.state}
          </span>
        </div>

        <div className="divide-y divide-gray-100">
          {order.lines.map((line) => (
            <div key={line.id} className="py-3 flex justify-between text-sm">
              <span className="text-gray-600">
                Variant #{line.variant_id ?? "?"} × {line.qty}
                <span className="text-gray-400 ml-2">(${line.unit_price.toFixed(2)} each)</span>
              </span>
              <span className="font-medium">${line.subtotal.toFixed(2)}</span>
            </div>
          ))}
        </div>

        <div className="border-t border-gray-100 mt-3 pt-3 space-y-1">
          {order.coupon_discount > 0 && (
            <div className="flex justify-between text-sm text-green-600">
              <span>Coupon discount</span>
              <span>−${order.coupon_discount.toFixed(2)}</span>
            </div>
          )}
          <div className="flex justify-between font-bold text-gray-800 text-lg">
            <span>Total</span>
            <span>${order.total_amount.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
