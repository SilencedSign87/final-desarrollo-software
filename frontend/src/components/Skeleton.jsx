export default function Skeleton({ className = '', children }) {
    return (
        <div className={`animate-shimmer bg-gray-300 rounded-md ${className}`}>
            {children}
        </div>
    )
}