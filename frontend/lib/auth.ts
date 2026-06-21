export const TOKEN_KEY = "cbp_access_token";

export function getToken() {
  if (typeof document === "undefined") return "";
  const cookies = document.cookie.split(";").map((item) => item.trim());
  const matched = cookies.find((item) => item.startsWith(`${TOKEN_KEY}=`));
  return matched ? decodeURIComponent(matched.split("=").slice(1).join("=")) : "";
}

export function setToken(token: string) {
  if (typeof document === "undefined") return;
  document.cookie = `${TOKEN_KEY}=${encodeURIComponent(token)}; path=/; max-age=${60 * 60 * 24 * 7}`;
}

export function clearToken() {
  if (typeof document === "undefined") return;
  document.cookie = `${TOKEN_KEY}=; path=/; max-age=0`;
}

export function isLoggedIn() {
  return Boolean(getToken());
}
