import "./globals.css";
import { getServerLanguage } from "@/lib/i18n-server";

export const metadata = {
  title: "商航AI",
  description: "AI驱动的跨境电商决策系统"
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const lang = await getServerLanguage();
  return (
    <html lang={lang === "en" ? "en" : "zh-CN"}>
      <body>{children}</body>
    </html>
  );
}
