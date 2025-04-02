"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/utils/auth";
import { usePathname, useRouter } from "next/navigation";

interface ProtectedComponentProps {
  children: React.ReactNode;
  requireVerified?: boolean;
}

const ProtectedComponent: React.FC<ProtectedComponentProps> = ({
  children,
  requireVerified = true,
}) => {
  const router = useRouter();
  const { token, isVerified } = useAuth();
  const pathname = usePathname();
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    if (!token) {
      router.push("/login?sourcePage=" + encodeURIComponent(pathname));
      return;
    }

    if (requireVerified && !isVerified) {
      router.push("/verification-required");
    }
  }, [token, isVerified, requireVerified, pathname, router]);

  // This is to prevent the page from starting to load the children before the token is checked
  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!token || (requireVerified && !isVerified) || !isClient) {
    return null;
  } else {
    return <>{children}</>;
  }
};

export { ProtectedComponent };
