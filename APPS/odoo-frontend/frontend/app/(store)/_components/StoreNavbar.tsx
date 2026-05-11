"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useCart } from "@/lib/cart";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function StoreNavbar() {
  const router = useRouter();
  const { totalItems } = useCart();
  const [userEmail, setUserEmail] = useState<string | null>(null);

  useEffect(() => {
    const match = document.cookie.match(/access_token=([^;]+)/);
    if (!match) return;
    fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${match[1]}` },
    })
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => data?.email && setUserEmail(data.email))
      .catch(() => {});
  }, []);

  function handleLogout() {
    document.cookie = "access_token=; path=/; max-age=0";
    setUserEmail(null);
    router.push("/store");
    router.refresh();
  }

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-6">
        <Link href="/store" className="text-lg font-bold text-indigo-600">
          Shop
        </Link>
        <Link
          href="/store"
          className="text-sm text-gray-600 hover:text-indigo-600"
        >
          Products
        </Link>
      </div>

      <div className="flex items-center gap-4">
        <Link href="/store/cart" className="relative text-gray-600 hover:text-indigo-600">
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13l-1.4 7h12.8M7 13L5.4 5M10 21a1 1 0 100-2 1 1 0 000 2zm7 0a1 1 0 100-2 1 1 0 000 2z"
            />
          </svg>
          {totalItems > 0 && (
            <span className="absolute -top-2 -right-2 bg-indigo-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
              {totalItems}
            </span>
          )}
        </Link>

        {userEmail ? (
          <div className="flex items-center gap-3">
            <Link
              href="/store/orders"
              className="text-sm text-gray-600 hover:text-indigo-600"
            >
              {userEmail}
            </Link>
            <button
              onClick={handleLogout}
              className="text-sm text-gray-500 hover:text-red-600"
            >
              Logout
            </button>
          </div>
        ) : (
          <Link
            href="/store/login"
            className="text-sm bg-indigo-600 text-white px-3 py-1.5 rounded hover:bg-indigo-700"
          >
            Login
          </Link>
        )}
      </div>
    </nav>
  );
}
