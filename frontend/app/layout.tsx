import "./globals.css";

export const metadata = {
  title: "XBorder AI 决策流系统",
  description: "AI驱动的跨境电商单决策流工作台"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
