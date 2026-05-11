import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Odoo Frontend",
  description: "Odoo-style dashboard for WMS, Ecommerce, and Users",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
