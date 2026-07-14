export default function Spinner({ size = 40, strokeWidth = 4, color = '#3B82F6' }) {
  return (
    <span className="inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="spinner-rotate"
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={(size - strokeWidth) / 2}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          className="spinner-dash"
        />
      </svg>
    </span>
  );
}