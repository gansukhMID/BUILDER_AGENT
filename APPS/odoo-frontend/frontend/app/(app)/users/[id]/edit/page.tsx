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
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export default function EditUserPage() {
  const router = useRouter();
  const { id } = useParams<{ id: string }>();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [userForm, setUserForm] = useState({
    email: "",
    is_active: true,
    is_verified: false,
    is_superuser: false,
  });
  const [profileForm, setProfileForm] = useState({
    display_name: "",
    bio: "",
    phone: "",
    timezone: "UTC",
    locale: "en",
  });
  const [hasProfile, setHasProfile] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(`${API_BASE}/users/${id}`, { headers: authHeaders() });
        if (!res.ok) throw new Error("User not found");
        const data = await res.json();
        setUserForm({
          email: data.email,
          is_active: data.is_active,
          is_verified: data.is_verified ?? false,
          is_superuser: data.is_superuser ?? false,
        });
        if (data.profile) {
          setHasProfile(true);
          setProfileForm({
            display_name: data.profile.display_name ?? "",
            bio: data.profile.bio ?? "",
            phone: data.profile.phone ?? "",
            timezone: data.profile.timezone ?? "UTC",
            locale: data.profile.locale ?? "en",
          });
        }
      } catch (err) {
        setError(String(err instanceof Error ? err.message : err));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  function handleUser(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    const { name, value } = e.target;
    const type = (e.target as HTMLInputElement).type;
    const checked = (e.target as HTMLInputElement).checked;
    setUserForm((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
  }

  function handleProfile(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    const { name, value } = e.target;
    setProfileForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const userRes = await fetch(`${API_BASE}/users/${id}`, {
        method: "PUT",
        headers: authHeaders(),
        body: JSON.stringify(userForm),
      });
      if (!userRes.ok) {
        const data = await userRes.json().catch(() => ({}));
        throw new Error(data.detail ?? `Error ${userRes.status}`);
      }

      const profilePayload = Object.fromEntries(
        Object.entries(profileForm).filter(([, v]) => v !== "")
      );
      if (Object.keys(profilePayload).length > 0) {
        const method = hasProfile ? "PUT" : "POST";
        await fetch(`${API_BASE}/users/${id}/profile`, {
          method,
          headers: authHeaders(),
          body: JSON.stringify(profilePayload),
        });
      }

      router.push(`/users/${id}`);
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
        <Link href={`/users/${id}`} className="text-gray-500 hover:text-gray-700 text-sm">
          ← User
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Edit User</h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
          <h2 className="font-semibold text-gray-700">Account</h2>
          <FormField label="Email" name="email" type="email" value={userForm.email} onChange={handleUser} required />
          <div className="flex flex-col gap-2">
            {(["is_active", "is_verified", "is_superuser"] as const).map((field) => (
              <label key={field} className="flex items-center gap-2 text-sm text-gray-700">
                <input
                  type="checkbox"
                  name={field}
                  checked={userForm[field]}
                  onChange={handleUser}
                  className="rounded border-gray-300"
                />
                {field.replace("is_", "").replace("_", " ").replace(/^\w/, (c) => c.toUpperCase())}
              </label>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
          <h2 className="font-semibold text-gray-700">Profile</h2>
          <FormField label="Display Name" name="display_name" value={profileForm.display_name} onChange={handleProfile} />
          <FormField label="Phone" name="phone" value={profileForm.phone} onChange={handleProfile} />
          <FormField label="Bio" name="bio" value={profileForm.bio} onChange={handleProfile} as="textarea" />
          <FormField label="Timezone" name="timezone" value={profileForm.timezone} onChange={handleProfile} />
          <FormField label="Locale" name="locale" value={profileForm.locale} onChange={handleProfile} />
        </div>

        {error && <p className="text-red-600 text-sm">{error}</p>}

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save Changes"}
          </button>
          <Link
            href={`/users/${id}`}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50"
          >
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
