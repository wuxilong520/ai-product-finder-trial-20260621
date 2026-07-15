import { NextRequest, NextResponse } from "next/server";

const TOKEN_KEY = "cbp_access_token";

const PUBLIC_PATHS = [
  "/login",
  "/register",
  "/forgot-password",
  "/terms",
  "/privacy",
  "/service-policy",
];

const PUBLIC_PREFIXES = [
  "/_next",
  "/api",
  "/favicon.ico",
  "/robots.txt",
  "/sitemap.xml",
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (PUBLIC_PREFIXES.some((prefix) => pathname.startsWith(prefix)) || PUBLIC_PATHS.includes(pathname)) {
    return NextResponse.next();
  }

  const token = request.cookies.get(TOKEN_KEY)?.value;
  if (!token) {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = "/login";
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image).*)"],
};
