import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const ADMIN_PROTECTED = /^\/(dashboard|wms|ecommerce|users)(\/|$)/;
const STORE_PROTECTED = /^\/store\/(checkout|orders)(\/|$)/;
const ADMIN_LOGIN = "/login";
const STORE_LOGIN = "/store/login";

export function middleware(request: NextRequest) {
  const token = request.cookies.get("access_token")?.value;
  const { pathname } = request.nextUrl;

  // Admin routes — redirect to /login
  if (ADMIN_PROTECTED.test(pathname)) {
    if (!token) {
      return NextResponse.redirect(new URL(ADMIN_LOGIN, request.url));
    }
  }

  // Admin login page — redirect to dashboard if already authed
  if (pathname === ADMIN_LOGIN && token) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  // Store protected routes — redirect to /store/login
  if (STORE_PROTECTED.test(pathname) && !token) {
    const next = encodeURIComponent(pathname);
    return NextResponse.redirect(
      new URL(`${STORE_LOGIN}?next=${next}`, request.url)
    );
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
