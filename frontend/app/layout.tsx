import "./globals.css";

export const metadata = {
  title: "AI Product Finder SaaS",
  description: "Cross-border product intelligence workspace"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
