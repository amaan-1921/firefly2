// src/auth.ts
import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import { z } from "zod";
import { authConfig } from "../auth.config";

export const authOptions = {
  ...authConfig,
  providers: [
    CredentialsProvider({
      name: "Email",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        const parsed = z
          .object({
            email: z.string().email(),
            password: z.string().min(6),
          })
          .safeParse(credentials);

        if (!parsed.success) return null;

        const { email, password } = parsed.data;

        // Demo user; replace with real DB lookup
        if (email === "user1@company.com" && password === "password123") {
          return {
            id: "1",
            name: "User One",
            email,
            role: "manager",
          };
        }

        return null;
      },
    }),
  ],
};

export default NextAuth(authOptions);
