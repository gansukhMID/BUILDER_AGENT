interface Location {
  id: number;
  name: string;
  complete_name: string;
  location_type: string;
}

async function getLocations(): Promise<Location[]> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  try {
    const res = await fetch(`${base}/wms/locations`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

function getDepth(completeName: string): number {
  return (completeName.match(/\//g) || []).length;
}

export default async function LocationsPage() {
  const locations = await getLocations();

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Locations</h1>
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        {locations.length === 0 ? (
          <p className="text-gray-400 text-sm text-center py-8">No locations found.</p>
        ) : (
          <ul className="space-y-1">
            {locations.map((loc) => {
              const depth = getDepth(loc.complete_name);
              return (
                <li
                  key={loc.id}
                  className="flex items-center gap-2 py-1 text-sm text-gray-700"
                  style={{ paddingLeft: `${depth * 20 + 8}px` }}
                >
                  <span className="text-gray-400">▸</span>
                  <span className="font-medium">{loc.name}</span>
                  <span className="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">
                    {loc.location_type}
                  </span>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
