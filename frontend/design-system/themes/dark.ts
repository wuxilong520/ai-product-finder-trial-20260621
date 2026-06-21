import { colors } from "@/design-system/colors";

export const darkTheme = {
  colors,
  radius: {
    sm: "12px",
    md: "16px",
    lg: "16px",
    xl: "16px",
  },
  shadow: {
    soft: "0 18px 48px rgba(2, 6, 23, 0.28)",
    deep: "0 28px 90px rgba(2, 6, 23, 0.45)",
    glow: "0 0 0 1px rgba(108, 92, 231, 0.16), 0 0 40px rgba(108, 92, 231, 0.18)",
  },
} as const;
