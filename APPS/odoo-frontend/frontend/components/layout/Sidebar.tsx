"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const nav = [
  {
    label: "Dashboard",
    href: "/dashboard",
    icon: "⊞",
  },
  {
    label: "WMS",
    icon: "🏭",
    children: [
      { label: "Warehouses", href: "/wms" },
      { label: "Locations", href: "/wms/locations" },
      { label: "Inventory", href: "/wms/inventory" },
      { label: "Pickings", href: "/wms/pickings" },
      { label: "Picking Types", href: "/wms/picking-types" },
    ],
  },
  {
    label: "Ecommerce",
    icon: "🛒",
    children: [
      { label: "Products", href: "/ecommerce" },
      { label: "Orders", href: "/ecommerce/orders" },
      { label: "Coupons", href: "/ecommerce/coupons" },
      { label: "Categories", href: "/ecommerce/categories" },
      { label: "Shipping", href: "/ecommerce/shipping-methods" },
    ],
  },
  {
    label: "Users",
    icon: "👥",
    children: [
      { label: "All Users", href: "/users" },
    ],
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-60 min-h-screen bg-gray-900 text-gray-100 flex flex-col">
      <div className="px-4 py-5 border-b border-gray-700">
        <span className="font-bold text-lg tracking-tight">Odoo Frontend</span>
      </div>
      <nav className="flex-1 overflow-y-auto py-4">
        {nav.map((item) => (
          <div key={item.label} className="mb-1">
            {item.href ? (
              <Link
                href={item.href}
                className={`flex items-center gap-2 px-4 py-2 text-sm rounded mx-2 ${
                  pathname === item.href
                    ? "bg-blue-600 text-white"
                    : "text-gray-300 hover:bg-gray-700"
                }`}
              >
                <span>{item.icon}</span>
                {item.label}
              </Link>
            ) : (
              <>
                <div className="flex items-center gap-2 px-4 py-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  <span>{item.icon}</span>
                  {item.label}
                </div>
                {item.children?.map((child) => (
                  <Link
                    key={child.href}
                    href={child.href}
                    className={`flex items-center pl-10 pr-4 py-1.5 text-sm rounded mx-2 ${
                      pathname === child.href || pathname.startsWith(child.href + "/")
                        ? "bg-blue-600 text-white"
                        : "text-gray-300 hover:bg-gray-700"
                    }`}
                  >
                    {child.label}
                  </Link>
                ))}
              </>
            )}
          </div>
        ))}
      </nav>
    </aside>
  );
}
