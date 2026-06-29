import "./globals.css";
import { getServerLanguage } from "@/lib/i18n-server";

export const metadata = {
  title: "XBorder AI 决策流系统",
  description: "AI驱动的跨境电商单决策流工作台"
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const lang = await getServerLanguage();
  return (
    <html lang={lang === "en" ? "en" : "zh-CN"}>
      <body>{children}</body>
    </html>
  );
}
