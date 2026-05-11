"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import FormField from "@/components/ui/FormField";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(/access_token=([^;]+)/);
  return match ? match[1] : null;
}

export default function NewCouponPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    code: "",
    discount_type: "percentage",
    discount_value: "10",
    min_order_amount: "0",
    usage_limit: "",
    expiry_date: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const token = getToken();
      const res = await fetch(`${API_BASE}/ecommerce/coupons`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          code: form.code,
          discount_type: form.discount_type,
          discount_value: parseFloat(form.discount_value),
          min_order_amount: parseFloat(form.min_order_amount) || 0,
          usage_limit: form.usage_limit ? parseInt(form.usage_limit) : null,
          expiry_date: form.expiry_date || null,
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

  return (
    <div className="max-w-lg">
      <div className="flex items-center gap-3 mb-6">
        <Link href="/ecommerce/coupons" className="text-gray-500 hover:text-gray-700 text-sm">← Coupons</Link>
        <h1 className="text-2xl font-bold text-gray-900">New Coupon</h1>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
        <FormField label="Code" name="code" value={form.code} onChange={handleChange} required placeholder="SAVE10" />
        <FormField label="Discount Type" name="discount_type" value={form.discount_type} onChange={handleChange} as="select">
          <option value="percentage">Percentage (%)</option>
          <option value="fixed">Fixed Amount</option>
        </FormField>
        <FormField label="Discount Value" name="discount_value" type="number" value={form.discount_value} onChange={handleChange} required />
        <FormField label="Min Order Amount" name="min_order_amount" type="number" value={form.min_order_amount} onChange={handleChange} />
        <FormField label="Usage Limit (leave blank for unlimited)" name="usage_limit" type="number" value={form.usage_limit} onChange={handleChange} />
        <FormField label="Expiry Date" name="expiry_date" type="date" value={form.expiry_date} onChange={handleChange} />

        {error && <p className="text-red-600 text-sm">{error}</p>}

        <div className="flex gap-3 pt-2">
          <button type="submit" disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
            {saving ? "Creating..." : "Create Coupon"}
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
