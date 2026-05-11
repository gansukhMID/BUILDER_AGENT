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

interface Variant { id: number; sku: string | null; default_price: number | null; }

export default function EditProductPage() {
  const router = useRouter();
  const { id } = useParams<{ id: string }>();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ name: "", list_price: "0", description: "", image_url: "" });
  const [variants, setVariants] = useState<Variant[]>([]);
  const [newVariant, setNewVariant] = useState({ sku: "", default_price: "0" });

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(`${API_BASE}/ecommerce/products/${id}`, { headers: authHeaders() });
        if (!res.ok) throw new Error("Product not found");
        const data = await res.json();
        setForm({
          name: data.name,
          list_price: String(data.list_price),
          description: data.description ?? "",
          image_url: data.image_url ?? "",
        });
        setVariants(data.variants ?? []);
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
      const res = await fetch(`${API_BASE}/ecommerce/products/${id}`, {
        method: "PUT",
        headers: authHeaders(),
        body: JSON.stringify({
          name: form.name,
          list_price: parseFloat(form.list_price) || 0,
          description: form.description || null,
          image_url: form.image_url || null,
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail ?? `Error ${res.status}`);
      }
      router.push("/ecommerce");
    } catch (err) {
      setError(String(err instanceof Error ? err.message : err));
    } finally {
      setSaving(false);
    }
  }

  async function handleAddVariant(e: React.FormEvent) {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/ecommerce/products/${id}/variants`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({
          sku: newVariant.sku || null,
          default_price: parseFloat(newVariant.default_price) || 0,
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail ?? `Error ${res.status}`);
      }
      const added: Variant = await res.json();
      setVariants((prev) => [...prev, added]);
      setNewVariant({ sku: "", default_price: "0" });
    } catch (err) {
      setError(String(err instanceof Error ? err.message : err));
    }
  }

  if (loading) return <p className="text-gray-500 text-sm">Loading...</p>;

  return (
    <div className="max-w-lg">
      <div className="flex items-center gap-3 mb-6">
        <Link href="/ecommerce" className="text-gray-500 hover:text-gray-700 text-sm">← Products</Link>
        <h1 className="text-2xl font-bold text-gray-900">Edit Product</h1>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-gray-200 p-6 space-y-4 mb-6">
        <FormField label="Name" name="name" value={form.name} onChange={handleChange} required />
        <FormField label="Price" name="list_price" type="number" value={form.list_price} onChange={handleChange} required />
        <FormField label="Description" name="description" value={form.description} onChange={handleChange} as="textarea" />
        <FormField label="Image URL" name="image_url" value={form.image_url} onChange={handleChange} />

        {error && <p className="text-red-600 text-sm">{error}</p>}

        <div className="flex gap-3 pt-2">
          <button type="submit" disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
            {saving ? "Saving..." : "Save Changes"}
          </button>
          <Link href="/ecommerce"
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50">
            Cancel
          </Link>
        </div>
      </form>

      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="font-semibold text-gray-700 mb-4">Variants ({variants.length})</h2>
        {variants.length > 0 && (
          <ul className="mb-4 space-y-1 text-sm">
            {variants.map((v) => (
              <li key={v.id} className="flex items-center justify-between py-1 border-b border-gray-100">
                <span className="font-mono text-gray-700">{v.sku ?? "(no SKU)"}</span>
                <span className="text-gray-500">${v.default_price?.toFixed(2)}</span>
              </li>
            ))}
          </ul>
        )}
        <form onSubmit={handleAddVariant} className="flex gap-2 items-end">
          <div className="flex-1">
            <FormField label="SKU" name="sku" value={newVariant.sku}
              onChange={(e) => setNewVariant((p) => ({ ...p, sku: e.target.value }))} />
          </div>
          <div className="w-28">
            <FormField label="Price" name="default_price" type="number" value={newVariant.default_price}
              onChange={(e) => setNewVariant((p) => ({ ...p, default_price: e.target.value }))} />
          </div>
          <button type="submit"
            className="px-3 py-2 bg-green-600 text-white rounded-md text-sm hover:bg-green-700 mb-0">
            + Add
          </button>
        </form>
      </div>
    </div>
  );
}
