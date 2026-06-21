export const colors = {
  background: {
    primary: "#0B0F1A",
    secondary: "#0E1424",
    tertiary: "#111827",
    surface: "rgba(255,255,255,0.06)",
    surfaceStrong: "rgba(255,255,255,0.10)",
    surfaceSoft: "rgba(255,255,255,0.04)",
  },
  brand: {
    primary: "#6C5CE7",
    secondary: "#00D2FF",
    accent: "#7C3AED",
    primarySoft: "rgba(108,92,231,0.18)",
    secondarySoft: "rgba(0,210,255,0.18)",
    accentSoft: "rgba(124,58,237,0.18)",
  },
  text: {
    primary: "#F8FAFC",
    secondary: "#CBD5E1",
    muted: "#94A3B8",
    dark: "#0F172A",
  },
  border: {
    soft: "rgba(255,255,255,0.10)",
    strong: "rgba(255,255,255,0.16)",
    glow: "rgba(108,92,231,0.32)",
  },
  feedback: {
    running: "#14B8A6",
    success: "#22C55E",
    warning: "#F59E0B",
    danger: "#F43F5E",
    blocked: "#64748B",
    info: "#38BDF8",
  },
  radius: {
    sm: "12px",
    md: "16px",
  },
} as const;

export type AppColors = typeof colors;
