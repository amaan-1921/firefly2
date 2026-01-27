// src/app/LoginForm.tsx
"use client";

import { useState, useTransition } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { signIn } from "next-auth/react";
import Image from "next/image";
import { Mail, Lock, Eye, EyeOff } from "lucide-react";

export default function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const callbackUrl = searchParams.get("callbackUrl") ?? "/dashboard";

  const [email, setEmail] = useState("user1@company.com");
  const [password, setPassword] = useState("password123");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    startTransition(async () => {
      const res = await signIn("credentials", {
        email,
        password,
        redirect: false,
        callbackUrl,
      });

      if (res?.error) {
        setError("Invalid email or password.");
      } else if (res?.url) {
        router.push(res.url);
      }
    });
  };

  const toggleShowPassword = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row font-sans">
      {/* Left: Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Header */}
          <div className="flex items-center mb-8">
            <h1 className="text-4xl font-bold text-red-600">ADAPT</h1>
            <svg
              className="ml-2 w-6 h-6 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
              />
            </svg>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Input */}
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                id="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                required
              />
            </div>

            {/* Password Input */}
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                className="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                required
              />
              <button
                type="button"
                onClick={toggleShowPassword}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>

            {/* Error Message */}
            {error && (
              <p className="text-sm text-red-600 text-center">{error}</p>
            )}

            {/* Sign In Button */}
            <button
              type="submit"
              className="w-full bg-red-500 text-white py-3 rounded-full font-medium hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50"
              disabled={isPending}
            >
              {isPending ? "Signing in..." : "Sign In via SSO"}
            </button>

            {/* Demo Credentials */}
            <p className="text-xs text-gray-400 text-center">
              Demo credentials: user1@company.com / password123
            </p>
          </form>

          {/* Footer */}
          <div className="text-center mt-6">
            <a href="#" className="text-sm text-gray-500 hover:text-gray-700">
              Forgot Password?
            </a>
          </div>
        </div>
      </div>

      {/* Right: Illustration */}
      <div className="hidden lg:flex flex-1 bg-slate-50 relative">
        <Image
          src="/illustration.png"
          alt="ADAPT Illustration"
          fill
          className="object-cover"
        />
      </div>
    </div>
  );
}