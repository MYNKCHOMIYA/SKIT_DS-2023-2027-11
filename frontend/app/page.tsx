import { redirect } from "next/navigation";

/**
 * Root page — redirects unauthenticated users to /login.
 * Sprint 2 will add dashboard detection based on JWT presence.
 */
export default function RootPage() {
  redirect("/login");
}
