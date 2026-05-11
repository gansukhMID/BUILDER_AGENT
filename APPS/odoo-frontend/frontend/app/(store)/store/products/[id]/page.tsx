"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useCart } from "@/lib/cart";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface Variant {
  id: number;
  sku: string | null;
  default_price: number;
}

interface ProductDetail {
  id: number;
  name: string;
  list_price: number;
  variants: Variant[];
}

export default function ProductDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { addItem } = useCart();
  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [selectedVariant, setSelectedVariant] = useState<Variant | null>(null);
  const [added, setAdded] = useState(false);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE}/store/products/${id}`)
      .then((r) => {
        if (r.status === 404) { setNotFound(true); return null; }
        return r.json();
      })
      .then((data) => {
        if (!data) return;
        setProduct(data);
        if (data.variants.length > 0) setSelectedVariant(data.variants[0]);
      })
      .catch(() => setNotFound(true));
  }, [id]);

  function handleAddToCart() {
    if (!product || !selectedVariant) return;
    addItem({
      variantId: selectedVariant.id,
      variantSku: selectedVariant.sku,
      productName: product.name,
      unitPrice: selectedVariant.default_price,
    });
    setAdded(true);
    setTimeout(() => setAdded(false), 2000);
  }

  if (notFound) {
    return (
      <div className="text-center py-16">
        <p className="text-gray-500 text-lg">Product not found.</p>
        <Link href="/store" className="mt-4 inline-block text-indigo-600 hover:underline">
          Back to store
        </Link>
      </div>
    );
  }

  if (!product) {
    return <div className="text-gray-400 py-8">Loading...</div>;
  }

  return (
    <div>
      <nav className="text-sm text-gray-500 mb-6">
        <Link href="/store" className="hover:text-indigo-600">Shop</Link>
        <span className="mx-2">›</span>
        <span className="text-gray-800">{product.name}</span>
      </nav>

      <div className="bg-white rounded-lg border border-gray-200 p-8 max-w-xl">
        <h1 className="text-2xl font-bold text-gray-800">{product.name}</h1>
        <p className="text-3xl font-bold text-indigo-600 mt-2">
          ${(selectedVariant?.default_price ?? product.list_price).toFixed(2)}
        </p>

        {product.variants.length > 0 && (
          <div className="mt-6">
            <p className="text-sm font-medium text-gray-700 mb-2">Select variant</p>
            <div className="space-y-2">
              {product.variants.map((v) => (
                <label
                  key={v.id}
                  className={`flex items-center gap-3 p-3 rounded border cursor-pointer transition-colors ${
                    selectedVariant?.id === v.id
                      ? "border-indigo-500 bg-indigo-50"
                      : "border-gray-200 hover:border-indigo-300"
                  }`}
                >
                  <input
                    type="radio"
                    name="variant"
                    value={v.id}
                    checked={selectedVariant?.id === v.id}
                    onChange={() => setSelectedVariant(v)}
                    className="text-indigo-600"
                  />
                  <span className="text-sm text-gray-700">
                    {v.sku ?? `Variant #${v.id}`}
                  </span>
                  <span className="ml-auto text-sm font-semibold text-gray-800">
                    ${v.default_price.toFixed(2)}
                  </span>
                </label>
              ))}
            </div>
          </div>
        )}

        <button
          onClick={handleAddToCart}
          disabled={!selectedVariant}
          className={`mt-6 w-full py-3 rounded text-sm font-medium transition-colors ${
            added
              ? "bg-green-500 text-white"
              : "bg-indigo-600 text-white hover:bg-indigo-700"
          } disabled:opacity-40`}
        >
          {added ? "Added to cart!" : "Add to Cart"}
        </button>
      </div>
    </div>
  );
}
