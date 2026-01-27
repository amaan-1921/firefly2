// middleware.ts (project root)
import { withAuth } from "next-auth/middleware";

export default withAuth({
  callbacks: {
    authorized: ({ token, req }) => {
      const isOnDashboard = req.nextUrl.pathname.startsWith("/dashboard");
      if (isOnDashboard) {
        return !!token;
      }
      return true;
    },
  },
});

export const config = {
  matcher: ["/dashboard/:path*", "/monitoring/:path*", "/alerts/:path*", "/impact/:path*", "/recommendations/:path*", "/suppliers/:path*", "/settings/:path*"],
};
