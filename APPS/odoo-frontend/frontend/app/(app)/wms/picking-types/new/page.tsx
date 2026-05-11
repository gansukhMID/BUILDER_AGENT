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

export default function NewPickingTypePage() {
  const router = useRouter();
  const [form, setForm] = useState({ name: "", operation_type: "incoming", warehouse_id: "", sequence_prefix: "" });
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
      const res = await fetch(`${API_BASE}/wms/picking-types`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        body: JSON.stringify({
          name: form.name,
          operation_type: form.operation_type,
          warehouse_id: form.warehouse_id ? parseInt(form.warehouse_id) : null,
          sequence_prefix: form.sequence_prefix || null,
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail ?? `Error ${res.status}`);
      }
      router.push("/wms/picking-types");
    } catch (err) {
      setError(String(err instanceof Error ? err.message : err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="max-w-lg">
      <div className="flex items-center gap-3 mb-6">
        <Link href="/wms/picking-types" className="text-gray-500 hover:text-gray-700 text-sm">← Picking Types</Link>
        <h1 className="text-2xl font-bold text-gray-900">New Picking Type</h1>
      </div>
      <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
        <FormField label="Name" name="name" value={form.name} onChange={handleChange} required />
        <FormField label="Operation Type" name="operation_type" value={form.operation_type} onChange={handleChange} as="select">
          <option value="incoming">Incoming (Receipts)</option>
          <option value="outgoing">Outgoing (Deliveries)</option>
          <option value="internal">Internal Transfer</option>
        </FormField>
        <FormField label="Warehouse ID (optional)" name="warehouse_id" type="number" value={form.warehouse_id} onChange={handleChange} />
        <FormField label="Sequence Prefix (optional)" name="sequence_prefix" value={form.sequence_prefix} onChange={handleChange} placeholder="WH/IN/" />
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <div className="flex gap-3 pt-2">
          <button type="submit" disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
            {saving ? "Creating..." : "Create Picking Type"}
          </button>
          <Link href="/wms/picking-types"
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50">
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
