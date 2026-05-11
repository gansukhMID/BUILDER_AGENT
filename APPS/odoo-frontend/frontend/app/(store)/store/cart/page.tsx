"use client";

import Link from "next/link";
import { useCart } from "@/lib/cart";

export default function CartPage() {
  const { items, removeItem, updateQty, totalPrice } = useCart();

  if (items.length === 0) {
    return (
      <div className="text-center py-20">
        <p className="text-2xl text-gray-400 mb-4">Your cart is empty</p>
        <Link
          href="/store"
          className="inline-block bg-indigo-600 text-white px-6 py-2 rounded hover:bg-indigo-700 text-sm"
        >
          Browse Products
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Your Cart</h1>

      <div className="bg-white rounded-lg border border-gray-200 divide-y divide-gray-100">
        {items.map((item) => (
          <div key={item.variantId} className="flex items-center gap-4 p-4">
            <div className="flex-1 min-w-0">
              <p className="font-medium text-gray-800 truncate">{item.productName}</p>
              {item.variantSku && (
                <p className="text-xs text-gray-500">{item.variantSku}</p>
              )}
              <p className="text-sm text-indigo-600 font-semibold mt-0.5">
                ${item.unitPrice.toFixed(2)} each
              </p>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => updateQty(item.variantId, item.qty - 1)}
                className="w-7 h-7 rounded border border-gray-300 text-gray-600 hover:bg-gray-100 flex items-center justify-center text-lg leading-none"
              >
                −
              </button>
              <span className="w-8 text-center text-sm font-medium">{item.qty}</span>
              <button
                onClick={() => updateQty(item.variantId, item.qty + 1)}
                className="w-7 h-7 rounded border border-gray-300 text-gray-600 hover:bg-gray-100 flex items-center justify-center text-lg leading-none"
              >
                +
              </button>
            </div>

            <p className="w-20 text-right font-semibold text-gray-800">
              ${(item.unitPrice * item.qty).toFixed(2)}
            </p>

            <button
              onClick={() => removeItem(item.variantId)}
              className="text-gray-400 hover:text-red-500 transition-colors"
              aria-label="Remove"
            >
              ✕
            </button>
          </div>
        ))}
      </div>

      <div className="mt-6 flex items-center justify-between">
        <div>
          <p className="text-gray-500 text-sm">Total</p>
          <p className="text-2xl font-bold text-gray-800">${totalPrice.toFixed(2)}</p>
        </div>
        <Link
          href="/store/checkout"
          className="bg-indigo-600 text-white px-8 py-3 rounded font-medium hover:bg-indigo-700 text-sm"
        >
          Proceed to Checkout
        </Link>
      </div>
    </div>
  );
}
