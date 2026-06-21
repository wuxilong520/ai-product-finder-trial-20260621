import "./globals.css";
import { EnvGuard } from "@/components/system/env-guard";

export const metadata = {
  title: "AI Product Finder SaaS",
  description: "Cross-border product intelligence workspace"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>
        <EnvGuard>{children}</EnvGuard>
      </body>
    </html>
  );
}
