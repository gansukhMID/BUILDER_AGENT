interface StatCardProps {
  label: string;
  value: number | string;
  href?: string;
}

export default function StatCard({ label, value, href }: StatCardProps) {
  const content = (
    <div className="bg-white rounded-lg border border-gray-200 p-5 hover:shadow-sm transition-shadow">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
    </div>
  );
  if (href) {
    return <a href={href}>{content}</a>;
  }
  return content;
}
