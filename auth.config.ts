// auth.config.ts
export const authConfig: any = {
  pages: {
    signIn: "/login",
  },
  callbacks: {
    async jwt({ token, user }: any) {
      if (user) {
        token.id = user.id;
        token.role = user.role;
      }
      return token;
    },
    async session({ session, token }: any) {
      if (session.user) {
        session.user.id = token.id;
        session.user.role = token.role;
      }
      return session;
    },
    authorized({ auth, request: { nextUrl } }: any) {
      const isOnDashboard = nextUrl.pathname.startsWith("/dashboard");
      if (isOnDashboard) {
        return !!auth;
      }
      return true;
    },
  },
};
