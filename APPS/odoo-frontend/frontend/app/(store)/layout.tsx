import React from "react";
import { CartProvider } from "@/lib/cart";
import StoreNavbar from "./_components/StoreNavbar";

export default function StoreLayout({ children }: { children: React.ReactNode }) {
  return (
    <CartProvider>
      <div className="min-h-screen bg-gray-50">
        <StoreNavbar />
        <main className="max-w-6xl mx-auto px-4 py-8">{children}</main>
      </div>
    </CartProvider>
  );
}
