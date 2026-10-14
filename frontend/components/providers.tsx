"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"
import { type ThemeProviderProps } from "next-themes/dist/types"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { Toaster } from "sonner"
import { RoleProvider } from "@/components/role-provider"

export function Providers({ children, ...props }: ThemeProviderProps) {
  const [queryClient] = React.useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000,
            retry: 1,
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      <NextThemesProvider {...props}>
        <RoleProvider>{children}</RoleProvider>
        <Toaster position="top-center" richColors />
      </NextThemesProvider>
    </QueryClientProvider>
  )
}
