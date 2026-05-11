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

function authHeaders() {
  const token = getToken();
  return { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) };
}

interface MoveRow { product_id: string; location_src_id: string; location_dest_id: string; product_qty: string; }

export default function NewPickingPage() {
  const router = useRouter();
  const [form, setForm] = useState({ name: "", origin: "", scheduled_date: "", location_src_id: "", location_dest_id: "" });
  const [moves, setMoves] = useState<MoveRow[]>([]);
  const [newMove, setNewMove] = useState<MoveRow>({ product_id: "", location_src_id: "", location_dest_id: "", product_qty: "1" });
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function handleMoveChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    const { name, value } = e.target;
    setNewMove((prev) => ({ ...prev, [name]: value }));
  }

  function addMove() {
    if (!newMove.product_id || !newMove.location_src_id || !newMove.location_dest_id) return;
    setMoves((prev) => [...prev, { ...newMove }]);
    setNewMove({ product_id: "", location_src_id: "", location_dest_id: "", product_qty: "1" });
  }

  function removeMove(idx: number) {
    setMoves((prev) => prev.filter((_, i) => i !== idx));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/wms/pickings`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({
          name: form.name,
          origin: form.origin || null,
          scheduled_date: form.scheduled_date || null,
          location_src_id: form.location_src_id ? parseInt(form.location_src_id) : null,
          location_dest_id: form.location_dest_id ? parseInt(form.location_dest_id) : null,
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail ?? `Error ${res.status}`);
      }
      const picking = await res.json();

      for (const mv of moves) {
        await fetch(`${API_BASE}/wms/pickings/${picking.id}/moves`, {
          method: "POST",
          headers: authHeaders(),
          body: JSON.stringify({
            product_id: parseInt(mv.product_id),
            location_src_id: parseInt(mv.location_src_id),
            location_dest_id: parseInt(mv.location_dest_id),
            product_qty: parseFloat(mv.product_qty),
          }),
        });
      }

      router.push("/wms/pickings");
    } catch (err) {
      setError(String(err instanceof Error ? err.message : err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="max-w-2xl">
      <div className="flex items-center gap-3 mb-6">
        <Link href="/wms/pickings" className="text-gray-500 hover:text-gray-700 text-sm">← Pickings</Link>
        <h1 className="text-2xl font-bold text-gray-900">New Picking</h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
          <h2 className="font-semibold text-gray-700">Header</h2>
          <FormField label="Reference Name" name="name" value={form.name} onChange={handleChange} required placeholder="WH/OUT/0001" />
          <FormField label="Source Document" name="origin" value={form.origin} onChange={handleChange} placeholder="SO-1234" />
          <FormField label="Scheduled Date" name="scheduled_date" type="datetime-local" value={form.scheduled_date} onChange={handleChange} />
          <div className="grid grid-cols-2 gap-4">
            <FormField label="Source Location ID" name="location_src_id" type="number" value={form.location_src_id} onChange={handleChange} />
            <FormField label="Dest Location ID" name="location_dest_id" type="number" value={form.location_dest_id} onChange={handleChange} />
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-700 mb-4">Move Lines</h2>
          {moves.length > 0 && (
            <ul className="mb-4 space-y-1 text-sm">
              {moves.map((mv, i) => (
                <li key={i} className="flex items-center justify-between py-1 border-b border-gray-100">
                  <span className="text-gray-700">Product {mv.product_id} — {mv.product_qty} units — Loc {mv.location_src_id}→{mv.location_dest_id}</span>
                  <button type="button" onClick={() => removeMove(i)} className="text-red-500 text-xs hover:text-red-700">Remove</button>
                </li>
              ))}
            </ul>
          )}
          <div className="grid grid-cols-4 gap-2 items-end">
            <FormField label="Product ID" name="product_id" type="number" value={newMove.product_id} onChange={handleMoveChange} />
            <FormField label="From Loc ID" name="location_src_id" type="number" value={newMove.location_src_id} onChange={handleMoveChange} />
            <FormField label="To Loc ID" name="location_dest_id" type="number" value={newMove.location_dest_id} onChange={handleMoveChange} />
            <div>
              <FormField label="Qty" name="product_qty" type="number" value={newMove.product_qty} onChange={handleMoveChange} />
            </div>
          </div>
          <button type="button" onClick={addMove}
            className="mt-2 px-3 py-1.5 bg-green-600 text-white rounded text-sm hover:bg-green-700">
            + Add Move
          </button>
        </div>

        {error && <p className="text-red-600 text-sm">{error}</p>}

        <div className="flex gap-3">
          <button type="submit" disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
            {saving ? "Creating..." : "Create Picking"}
          </button>
          <Link href="/wms/pickings"
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50">
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
