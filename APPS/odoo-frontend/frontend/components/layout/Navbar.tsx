"use client";
import { useRouter } from "next/navigation";

export default function Navbar() {
  const router = useRouter();

  function logout() {
    document.cookie = "access_token=; path=/; max-age=0";
    router.push("/login");
  }

  return (
    <header className="h-12 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      <div />
      <button
        onClick={logout}
        className="text-sm text-gray-600 hover:text-gray-900"
      >
        Sign out
      </button>
    </header>
  );
}
