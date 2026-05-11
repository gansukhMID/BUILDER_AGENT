"use client";

import { useState, useEffect, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useCart } from "@/lib/cart";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(/access_token=([^;]+)/);
  return match ? match[1] : null;
}

interface CouponResult {
  valid: boolean;
  discount_type: string;
  discount_value: number;
}

export default function CheckoutPage() {
  const router = useRouter();
  const { items, totalPrice, clearCart } = useCart();

  const [couponCode, setCouponCode] = useState("");
  const [coupon, setCoupon] = useState<CouponResult | null>(null);
  const [couponError, setCouponError] = useState("");
  const [couponLoading, setCouponLoading] = useState(false);

  const [orderError, setOrderError] = useState("");
  const [placing, setPlacing] = useState(false);

  useEffect(() => {
    if (!getToken()) {
      const next = encodeURIComponent("/store/checkout");
      router.replace(`/store/login?next=${next}`);
    }
  }, [router]);

  if (items.length === 0) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-500 mb-4">Your cart is empty.</p>
        <Link href="/store" className="text-indigo-600 hover:underline">
          Browse Products
        </Link>
      </div>
    );
  }

  const discount = coupon
    ? coupon.discount_type === "percentage"
      ? (totalPrice * coupon.discount_value) / 100
      : Math.min(coupon.discount_value, totalPrice)
    : 0;

  const finalTotal = Math.max(0, totalPrice - discount);

  async function handleValidateCoupon(e: FormEvent) {
    e.preventDefault();
    if (!couponCode.trim()) return;
    setCouponLoading(true);
    setCouponError("");
    setCoupon(null);
    try {
      const res = await fetch(`${API_BASE}/store/coupons/validate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: couponCode.trim() }),
      });
      if (!res.ok) {
        setCouponError("Invalid or inactive coupon code");
        return;
      }
      const data: CouponResult = await res.json();
      setCoupon(data);
    } catch {
      setCouponError("Failed to validate coupon");
    } finally {
      setCouponLoading(false);
    }
  }

  async function handlePlaceOrder() {
    const token = getToken();
    if (!token) {
      router.push("/store/login?next=/store/checkout");
      return;
    }
    setPlacing(true);
    setOrderError("");
    try {
      const res = await fetch(`${API_BASE}/store/orders`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          lines: items.map((i) => ({ variant_id: i.variantId, qty: i.qty })),
          coupon_code: coupon ? couponCode.trim() : undefined,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        setOrderError(err.detail ?? "Failed to place order");
        return;
      }
      const order = await res.json();
      clearCart();
      router.push(`/store/orders/${order.id}`);
    } catch {
      setOrderError("Connection error. Is the backend running?");
    } finally {
      setPlacing(false);
    }
  }

  return (
    <div className="max-w-xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Checkout</h1>

      {/* Order Summary */}
      <div className="bg-white rounded-lg border border-gray-200 p-5 mb-6">
        <h2 className="font-semibold text-gray-700 mb-3">Order Summary</h2>
        <div className="space-y-2">
          {items.map((item) => (
            <div key={item.variantId} className="flex justify-between text-sm">
              <span className="text-gray-600">
                {item.productName}
                {item.variantSku ? ` (${item.variantSku})` : ""} × {item.qty}
              </span>
              <span className="font-medium">${(item.unitPrice * item.qty).toFixed(2)}</span>
            </div>
          ))}
        </div>
        <div className="border-t border-gray-100 mt-3 pt-3 space-y-1">
          <div className="flex justify-between text-sm text-gray-600">
            <span>Subtotal</span>
            <span>${totalPrice.toFixed(2)}</span>
          </div>
          {coupon && (
            <div className="flex justify-between text-sm text-green-600">
              <span>Discount ({coupon.discount_type === "percentage" ? `${coupon.discount_value}%` : `$${coupon.discount_value}`})</span>
              <span>−${discount.toFixed(2)}</span>
            </div>
          )}
          <div className="flex justify-between font-bold text-gray-800 text-lg pt-1">
            <span>Total</span>
            <span>${finalTotal.toFixed(2)}</span>
          </div>
        </div>
      </div>

      {/* Coupon */}
      <div className="bg-white rounded-lg border border-gray-200 p-5 mb-6">
        <h2 className="font-semibold text-gray-700 mb-3">Coupon Code</h2>
        <form onSubmit={handleValidateCoupon} className="flex gap-2">
          <input
            type="text"
            value={couponCode}
            onChange={(e) => setCouponCode(e.target.value)}
            placeholder="Enter coupon code"
            className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            type="submit"
            disabled={couponLoading || !couponCode.trim()}
            className="bg-gray-800 text-white px-4 py-2 rounded text-sm hover:bg-gray-700 disabled:opacity-50"
          >
            {couponLoading ? "..." : "Apply"}
          </button>
        </form>
        {couponError && (
          <p className="mt-2 text-sm text-red-600">{couponError}</p>
        )}
        {coupon && (
          <p className="mt-2 text-sm text-green-600">
            ✓ Coupon applied — {coupon.discount_type === "percentage" ? `${coupon.discount_value}% off` : `$${coupon.discount_value} off`}
          </p>
        )}
      </div>

      {/* Place Order */}
      {orderError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          {orderError}
        </div>
      )}
      <button
        onClick={handlePlaceOrder}
        disabled={placing}
        className="w-full bg-indigo-600 text-white py-3 rounded font-medium hover:bg-indigo-700 disabled:opacity-50 text-sm"
      >
        {placing ? "Placing order..." : `Place Order — $${finalTotal.toFixed(2)}`}
      </button>
    </div>
  );
}
