const colorMap: Record<string, string> = {
  draft: "bg-gray-100 text-gray-700",
  confirmed: "bg-blue-100 text-blue-700",
  in_progress: "bg-yellow-100 text-yellow-800",
  done: "bg-green-100 text-green-700",
  cancelled: "bg-red-100 text-red-700",
  pending: "bg-yellow-100 text-yellow-800",
  authorized: "bg-blue-100 text-blue-700",
  captured: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
  free: "bg-gray-100 text-gray-700",
  pro: "bg-blue-100 text-blue-700",
  vip: "bg-purple-100 text-purple-700",
  placed: "bg-blue-100 text-blue-700",
  shipped: "bg-indigo-100 text-indigo-700",
  delivered: "bg-green-100 text-green-700",
};

export default function Badge({ value }: { value: string }) {
  const cls = colorMap[value?.toLowerCase()] ?? "bg-gray-100 text-gray-700";
  return (
    <span className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${cls}`}>
      {value}
    </span>
  );
}
