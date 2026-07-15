export const TOKEN_KEY = "cbp_access_token";
export const REFRESH_TOKEN_KEY = "cbp_refresh_token";

function buildCookieOptions(maxAge: number) {
  const secure = typeof window !== "undefined" && window.location.protocol === "https:" ? "; secure" : "";
  return `path=/; max-age=${maxAge}; samesite=lax${secure}`;
}

export function getToken() {
  if (typeof document === "undefined") return "";
  const cookies = document.cookie.split(";").map((item) => item.trim());
  const matched = cookies.find((item) => item.startsWith(`${TOKEN_KEY}=`));
  return matched ? decodeURIComponent(matched.split("=").slice(1).join("=")) : "";
}

export function getRefreshToken() {
  if (typeof document === "undefined") return "";
  const cookies = document.cookie.split(";").map((item) => item.trim());
  const matched = cookies.find((item) => item.startsWith(`${REFRESH_TOKEN_KEY}=`));
  return matched ? decodeURIComponent(matched.split("=").slice(1).join("=")) : "";
}

export function setToken(token: string) {
  if (typeof document === "undefined") return;
  document.cookie = `${TOKEN_KEY}=${encodeURIComponent(token)}; ${buildCookieOptions(60 * 60 * 24 * 7)}`;
}

export function setRefreshToken(token: string) {
  if (typeof document === "undefined") return;
  document.cookie = `${REFRESH_TOKEN_KEY}=${encodeURIComponent(token)}; ${buildCookieOptions(60 * 60 * 24 * 30)}`;
}

export function clearToken() {
  if (typeof document === "undefined") return;
  document.cookie = `${TOKEN_KEY}=; ${buildCookieOptions(0)}`;
  document.cookie = `${REFRESH_TOKEN_KEY}=; ${buildCookieOptions(0)}`;
}

export function isLoggedIn() {
  return Boolean(getToken());
}
