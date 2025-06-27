interface LoadingTableRowsProps {
  count?: number;
}

export default function LoadingTableRows({ count = 5 }: LoadingTableRowsProps) {
  return (
    <>
      {[...Array(count)].map((_, i) => (
        <tr key={i} className="animate-pulse">
          {/* ID */}
          <td className="px-6 py-4 whitespace-nowrap">
            <div className="h-4 bg-gray-200 rounded w-20"></div>
          </td>
          {/* Date & Time */}
          <td className="px-6 py-4 whitespace-nowrap">
            <div className="h-4 bg-gray-200 rounded w-28"></div>
          </td>
          {/* Tool Name */}
          <td className="px-6 py-4 whitespace-nowrap">
            <div className="h-4 bg-gray-200 rounded w-32"></div>
          </td>
          {/* Status */}
          <td className="px-6 py-4 whitespace-nowrap">
            <div className="h-6 bg-gray-200 rounded-full w-20"></div>
          </td>
        </tr>
      ))}
    </>
  );
} 