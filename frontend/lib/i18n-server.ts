import { cookies } from "next/headers";

import { LANGUAGE_COOKIE, Language } from "@/lib/i18n";

export async function getServerLanguage(): Promise<Language> {
  const cookieStore = await cookies();
  const value = cookieStore.get(LANGUAGE_COOKIE)?.value;
  return value === "en" ? "en" : "zh";
}
