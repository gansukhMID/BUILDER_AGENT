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

export default function NewLocationPage() {
  const router = useRouter();
  const [form, setForm] = useState({ name: "", location_type: "internal", parent_id: "", code: "" });
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
      const res = await fetch(`${API_BASE}/wms/locations`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        body: JSON.stringify({
          name: form.name,
          location_type: form.location_type,
          parent_id: form.parent_id ? parseInt(form.parent_id) : null,
          code: form.code || null,
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail ?? `Error ${res.status}`);
      }
      router.push("/wms/locations");
    } catch (err) {
      setError(String(err instanceof Error ? err.message : err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="max-w-lg">
      <div className="flex items-center gap-3 mb-6">
        <Link href="/wms/locations" className="text-gray-500 hover:text-gray-700 text-sm">← Locations</Link>
        <h1 className="text-2xl font-bold text-gray-900">New Location</h1>
      </div>
      <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
        <FormField label="Name" name="name" value={form.name} onChange={handleChange} required />
        <FormField label="Type" name="location_type" value={form.location_type} onChange={handleChange} as="select">
          <option value="internal">Internal</option>
          <option value="view">View</option>
          <option value="customer">Customer</option>
          <option value="supplier">Supplier</option>
          <option value="transit">Transit</option>
          <option value="inventory">Inventory</option>
          <option value="production">Production</option>
        </FormField>
        <FormField label="Parent Location ID (optional)" name="parent_id" type="number" value={form.parent_id} onChange={handleChange} />
        <FormField label="Code (optional)" name="code" value={form.code} onChange={handleChange} />
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <div className="flex gap-3 pt-2">
          <button type="submit" disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
            {saving ? "Creating..." : "Create Location"}
          </button>
          <Link href="/wms/locations"
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50">
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
