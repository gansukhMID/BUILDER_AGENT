"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import FormField from "@/components/ui/FormField";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(/access_token=([^;]+)/);
  return match ? match[1] : null;
}

function authHeaders() {
  const token = getToken();
  return { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) };
}

export default function EditCouponPage() {
  const router = useRouter();
  const { id } = useParams<{ id: string }>();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    discount_value: "0",
    min_order_amount: "0",
    usage_limit: "",
    expiry_date: "",
    active: true,
  });
  const [code, setCode] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const coupons = await fetch(`${API_BASE}/ecommerce/coupons`, { headers: authHeaders() }).then((r) => r.json());
        const coupon = coupons.find((c: { id: number }) => c.id === parseInt(id));
        if (!coupon) throw new Error("Coupon not found");
        setCode(coupon.code);
        setForm({
          discount_value: String(coupon.discount_value),
          min_order_amount: String(coupon.min_order_amount ?? 0),
          usage_limit: coupon.usage_limit != null ? String(coupon.usage_limit) : "",
          expiry_date: coupon.expiry_date ?? "",
          active: coupon.active ?? true,
        });
      } catch (err) {
        setError(String(err instanceof Error ? err.message : err));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;
    setForm((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/ecommerce/coupons/${id}`, {
        method: "PUT",
        headers: authHeaders(),
        body: JSON.stringify({
          discount_value: parseFloat(form.discount_value),
          min_order_amount: parseFloat(form.min_order_amount) || 0,
          usage_limit: form.usage_limit ? parseInt(form.usage_limit) : null,
          expiry_date: form.expiry_date || null,
          active: form.active,
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail ?? `Error ${res.status}`);
      }
      router.push("/ecommerce/coupons");
    } catch (err) {
      setError(String(err instanceof Error ? err.message : err));
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <p className="text-gray-500 text-sm">Loading...</p>;

  return (
    <div className="max-w-lg">
      <div className="flex items-center gap-3 mb-6">
        <Link href="/ecommerce/coupons" className="text-gray-500 hover:text-gray-700 text-sm">← Coupons</Link>
        <h1 className="text-2xl font-bold text-gray-900">Edit Coupon <span className="text-gray-500 font-mono text-lg">{code}</span></h1>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
        <FormField label="Discount Value" name="discount_value" type="number" value={form.discount_value} onChange={handleChange} required />
        <FormField label="Min Order Amount" name="min_order_amount" type="number" value={form.min_order_amount} onChange={handleChange} />
        <FormField label="Usage Limit (blank = unlimited)" name="usage_limit" type="number" value={form.usage_limit} onChange={handleChange} />
        <FormField label="Expiry Date" name="expiry_date" type="date" value={form.expiry_date} onChange={handleChange} />
        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input type="checkbox" name="active" checked={form.active} onChange={handleChange} className="rounded border-gray-300" />
          Active
        </label>

        {error && <p className="text-red-600 text-sm">{error}</p>}

        <div className="flex gap-3 pt-2">
          <button type="submit" disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
            {saving ? "Saving..." : "Save Changes"}
          </button>
          <Link href="/ecommerce/coupons"
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50">
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
