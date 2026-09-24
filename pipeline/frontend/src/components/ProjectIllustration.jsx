// Document-turned-into-a-verified-result illustration used on each project
// card. Pure currentColor/white so it can be recolored per card via the
// wrapping element's `color`, and the "complete" checkmark badge is only
// drawn when the project has actually finished, rather than always showing.
export default function ProjectIllustration({ complete = false, className = '' }) {
  return (
    <svg
      viewBox="0 0 340 150"
      preserveAspectRatio="xMidYMid meet"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      role="img"
      aria-hidden="true"
      className={className}
    >
      <defs>
        <pattern id="proj-illus-grid" width="20" height="20" patternUnits="userSpaceOnUse">
          <path d="M20 0H0V20" stroke="currentColor" strokeOpacity="0.12" strokeWidth="1" />
        </pattern>
        <radialGradient id="proj-illus-fade" cx="0.6" cy="0.5" r="0.65">
          <stop offset="0" stopColor="#FFFFFF" stopOpacity="1" />
          <stop offset="1" stopColor="#FFFFFF" stopOpacity="0" />
        </radialGradient>
        <mask id="proj-illus-mask">
          <rect width="340" height="150" fill="url(#proj-illus-fade)" />
        </mask>
      </defs>
      <rect width="340" height="150" fill="url(#proj-illus-grid)" stroke="none" mask="url(#proj-illus-mask)" />
      <g transform="rotate(-7 66 74)" strokeOpacity="0.45">
        <rect x="36" y="32" width="60" height="82" rx="5" fill="currentColor" fillOpacity="0.06" />
      </g>
      <path
        d="M50 26h40l16 16v72a5 5 0 0 1-5 5H50a5 5 0 0 1-5-5V31a5 5 0 0 1 5-5z"
        fill="#FFFFFF"
        fillOpacity="0.85"
      />
      <path d="M90 26v16h16" strokeWidth="1.6" />
      <path d="M55 52h30M55 62h40M55 72h24M55 82h36" strokeWidth="1.6" strokeOpacity="0.5" />
      <path d="M55 100h51h14" />
      <path d="M130 62h190" strokeDasharray="2 5" strokeWidth="1.2" strokeOpacity="0.55" />
      <path
        d="M120 100C140 100 146 38 164 38S184 82 198 82S216 52 228 52S244 68 254 68S268 60 278 60S296 62.5 318 62"
        strokeWidth="2.4"
      />
      <circle cx="164" cy="38" r="3.5" fill="#FFFFFF" />
      <circle cx="198" cy="82" r="3.5" fill="#FFFFFF" />
      <circle cx="228" cy="52" r="3.5" fill="#FFFFFF" />
      <circle cx="254" cy="68" r="3.5" fill="#FFFFFF" />
      <circle cx="120" cy="100" r="4" fill="currentColor" stroke="none" />
      {complete && (
        <>
          <circle cx="304" cy="30" r="12" fill="currentColor" stroke="none" />
          <path d="M298.5 30l4 4 7-7.5" stroke="#FFFFFF" strokeWidth="2.2" />
        </>
      )}
    </svg>
  )
}
