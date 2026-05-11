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

export default function EditWarehousePage() {
  const router = useRouter();
  const { id } = useParams<{ id: string }>();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ name: "", code: "", reception_steps: "one_step", delivery_steps: "one_step" });

  useEffect(() => {
    async function load() {
      try {
        const warehouses = await fetch(`${API_BASE}/wms/warehouses`, { headers: authHeaders() }).then((r) => r.json());
        const wh = warehouses.find((w: { id: number }) => w.id === parseInt(id));
        if (!wh) throw new Error("Warehouse not found");
        setForm({ name: wh.name, code: wh.code ?? "", reception_steps: wh.reception_steps ?? "one_step", delivery_steps: wh.delivery_steps ?? "one_step" });
      } catch (err) {
        setError(String(err instanceof Error ? err.message : err));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/wms/warehouses/${id}`, {
        method: "PUT",
        headers: authHeaders(),
        body: JSON.stringify({ ...form, code: form.code || null }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail ?? `Error ${res.status}`);
      }
      router.push("/wms");
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
        <Link href="/wms" className="text-gray-500 hover:text-gray-700 text-sm">← Warehouses</Link>
        <h1 className="text-2xl font-bold text-gray-900">Edit Warehouse</h1>
      </div>
      <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
        <FormField label="Name" name="name" value={form.name} onChange={handleChange} required />
        <FormField label="Code" name="code" value={form.code} onChange={handleChange} />
        <FormField label="Reception Steps" name="reception_steps" value={form.reception_steps} onChange={handleChange} as="select">
          <option value="one_step">One Step</option>
          <option value="two_steps">Two Steps</option>
          <option value="three_steps">Three Steps</option>
        </FormField>
        <FormField label="Delivery Steps" name="delivery_steps" value={form.delivery_steps} onChange={handleChange} as="select">
          <option value="one_step">One Step</option>
          <option value="two_steps">Two Steps</option>
          <option value="three_steps">Three Steps</option>
        </FormField>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <div className="flex gap-3 pt-2">
          <button type="submit" disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
            {saving ? "Saving..." : "Save Changes"}
          </button>
          <Link href="/wms"
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50">
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
