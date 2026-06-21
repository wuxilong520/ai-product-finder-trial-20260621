export const typography = {
  fontFamily: {
    sans: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },
  heading: {
    hero: "text-5xl md:text-6xl font-semibold tracking-tight",
    page: "text-3xl md:text-4xl font-semibold tracking-tight",
    section: "text-2xl font-semibold tracking-tight",
    card: "text-lg font-semibold tracking-tight",
  },
  body: {
    lg: "text-lg leading-8",
    md: "text-base leading-7",
    sm: "text-sm leading-6",
    xs: "text-xs leading-5 uppercase tracking-[0.18em]",
  },
} as const;
