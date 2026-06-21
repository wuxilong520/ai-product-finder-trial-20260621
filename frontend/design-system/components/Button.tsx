import * as React from "react";

import { cn } from "@/lib/utils";

const baseClass =
  "inline-flex items-center justify-center whitespace-nowrap rounded-2xl text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#6C5CE7]/60 disabled:pointer-events-none disabled:opacity-50";

const variantMap = {
  primary:
    "bg-app-brand-gradient text-white shadow-app-glow hover:-translate-y-0.5 hover:shadow-[0_0_0_1px_rgba(124,58,237,0.25),0_12px_40px_rgba(0,210,255,0.22)]",
  secondary:
    "border border-app-border bg-white/8 text-app-text-primary shadow-app-soft hover:-translate-y-0.5 hover:border-app-border-strong hover:bg-white/12",
  danger:
    "bg-[linear-gradient(135deg,#FB7185,#EF4444)] text-white hover:-translate-y-0.5 hover:shadow-[0_16px_40px_rgba(244,63,94,0.32)]",
  ghost: "bg-transparent text-app-text-secondary hover:bg-white/8 hover:text-white",
  default:
    "bg-app-brand-gradient text-white shadow-app-glow hover:-translate-y-0.5 hover:shadow-[0_0_0_1px_rgba(124,58,237,0.25),0_12px_40px_rgba(0,210,255,0.22)]",
  outline:
    "border border-app-border bg-white/8 text-app-text-primary shadow-app-soft hover:-translate-y-0.5 hover:border-app-border-strong hover:bg-white/12",
  destructive:
    "bg-[linear-gradient(135deg,#FB7185,#EF4444)] text-white hover:-translate-y-0.5 hover:shadow-[0_16px_40px_rgba(244,63,94,0.32)]",
} as const;

const sizeMap = {
  default: "h-11 px-5 py-2",
  sm: "h-9 px-3.5",
  lg: "h-12 px-6",
} as const;

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean;
  variant?: keyof typeof variantMap;
  size?: keyof typeof sizeMap;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "default", asChild = false, children, ...props }, ref) => {
    const classes = cn(baseClass, variantMap[variant], sizeMap[size], className);
    if (asChild && React.isValidElement(children)) {
      const child = children as React.ReactElement<{ className?: string }>;
      return React.cloneElement(child, {
        className: cn(classes, child.props.className),
      } as { className?: string });
    }
    return (
      <button className={classes} ref={ref} {...props}>
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";

export { Button };
