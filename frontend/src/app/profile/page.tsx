// src/app/profile/page.tsx
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/auth";

export const dynamic = 'force-dynamic';

export default async function ProfilePage() {
  const session = await getServerSession(authOptions) as any;

  if (!session?.user) {
    return (
      <div className="p-6">
        <p className="text-sm text-slate-500">
          You must be signed in to view your profile.
        </p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-xl font-semibold text-slate-900">
        User Profile
      </h1>
      <div className="rounded-xl border border-slate-200 bg-white p-4 space-y-2">
        <p className="text-sm">
          <span className="font-medium text-slate-600">Name:</span>{" "}
          {session.user.name}
        </p>
        <p className="text-sm">
          <span className="font-medium text-slate-600">Email:</span>{" "}
          {session.user.email}
        </p>
      </div>
    </div>
  );
}
