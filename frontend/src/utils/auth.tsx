"use client";
import { apiCalls } from "@/utils/api";
import { useRouter, useSearchParams } from "next/navigation";
import { ReactNode, createContext, useContext, useState, useEffect } from "react";

type Workspace = {
  workspace_id: number;
  workspace_name: string;
  api_key_first_characters: string;
  is_default: boolean;
};

type AuthContextType = {
  token: string | null;
  user: string | null;
  isVerified: boolean;
  isLoading: boolean;
  currentWorkspace: Workspace | null;
  workspaces: Workspace[];
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  loginError: string | null;
  switchWorkspace: (workspaceName: string) => Promise<void>;
  loginGoogle: ({
    client_id,
    credential,
  }: {
    client_id: string;
    credential: string;
  }) => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

type AuthProviderProps = {
  children: ReactNode;
};

const AuthProvider = ({ children }: AuthProviderProps) => {
  const getInitialToken = () => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("ee-token");
    }
    return null;
  };

  const getInitialUsername = () => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("ee-username");
    }
    return null;
  };

  const [user, setUser] = useState<string | null>(getInitialUsername);
  const [token, setToken] = useState<string | null>(getInitialToken);
  const [isVerified, setIsVerified] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(!!getInitialToken());
  const [loginError, setLoginError] = useState<string | null>(null);
  const [currentWorkspace, setCurrentWorkspace] = useState<Workspace | null>(null);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);

  const searchParams = useSearchParams();
  const router = useRouter();

  useEffect(() => {
    const loadWorkspaceInfo = async () => {
      if (token) {
        try {
          setIsLoading(true);
          // Fetch current workspace
          const currentWorkspaceData = await apiCalls.getCurrentWorkspace(token);
          setCurrentWorkspace(currentWorkspaceData);
          
          // Fetch all workspaces
          const workspacesData = await apiCalls.getAllWorkspaces(token);
          setWorkspaces(workspacesData);
        } catch (error) {
          console.error("Error loading workspace info:", error);
        } finally {
          setIsLoading(false);
        }
      }
    };

    loadWorkspaceInfo();
  }, [token]);

  // Check verification status on init if token exists
  useEffect(() => {
    const checkVerificationStatus = async () => {
      const currentToken = getInitialToken();
      if (currentToken) {
        setIsLoading(true);
        try {
          const userData = await apiCalls.getUser(currentToken);
          setIsVerified(userData.is_verified);
        } catch (error) {
          console.error("Error fetching user verification status:", error);
          logout();
        } finally {
          setIsLoading(false);
        }
      }
    };

    checkVerificationStatus();
  }, []);

  const login = async (username: string, password: string) => {
    const sourcePage = searchParams.has("sourcePage")
      ? decodeURIComponent(searchParams.get("sourcePage") as string)
      : "/";

    try {
      setIsLoading(true);
      const response = await apiCalls.getLoginToken(username, password);
      const { access_token } = response;

      localStorage.setItem("ee-token", access_token);
      localStorage.setItem("ee-username", username);

      setUser(username);
      setToken(access_token);
      setLoginError(null);

      // Check if verification status is in the response
      if (response.is_verified !== undefined) {
        setIsVerified(response.is_verified);
      } else {
        // If not in response, fetch user data to get verification status
        try {
          const userData = await apiCalls.getUser(access_token);
          setIsVerified(userData.is_verified);
        } catch (error) {
          console.error("Error fetching user verification status:", error);
        }
      }

      try {
        const currentWorkspaceData = await apiCalls.getCurrentWorkspace(access_token);
        setCurrentWorkspace(currentWorkspaceData);
        
        const workspacesData = await apiCalls.getAllWorkspaces(access_token);
        setWorkspaces(workspacesData);
      } catch (error) {
        console.error("Error loading workspace info:", error);
      }

      // Redirect to verification page if not verified, otherwise to original destination
      if (response.is_verified === false) {
        router.push("/verification-required");
      } else {
        router.push(sourcePage);
      }
    } catch (error: unknown) {
      if (
        error &&
        typeof error === "object" &&
        "status" in error &&
        error.status === 401
      ) {
        setLoginError("Invalid username or password");
      } else {
        setLoginError("An unexpected error occurred. Please try again later.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const switchWorkspace = async (workspaceName: string) => {
    try {
      setIsLoading(true);
      const response = await apiCalls.switchWorkspace(token, workspaceName);
      
      localStorage.setItem("ee-token", response.access_token);
      setToken(response.access_token);
      
      const currentWorkspaceData = await apiCalls.getCurrentWorkspace(response.access_token);
      setCurrentWorkspace(currentWorkspaceData);
      
      return response;
    } catch (error) {
      console.error("Error switching workspace:", error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const loginGoogle = async ({
    client_id,
    credential,
  }: {
    client_id: string;
    credential: string;
  }) => {
    const sourcePage = searchParams.has("sourcePage") && searchParams.get("sourcePage") != ""
      ? decodeURIComponent(searchParams.get("sourcePage") as string)
      : "/";

    try {
      setIsLoading(true);
      const response = await apiCalls.getGoogleLoginToken({
        client_id: client_id,
        credential: credential
      });

      const { access_token, username } = response;

      localStorage.setItem("ee-token", access_token);
      localStorage.setItem("ee-username", username);

      setUser(username);
      setToken(access_token);

      setIsVerified(true);

      try {
        const currentWorkspaceData = await apiCalls.getCurrentWorkspace(access_token);
        setCurrentWorkspace(currentWorkspaceData);
        
        const workspacesData = await apiCalls.getAllWorkspaces(access_token);
        setWorkspaces(workspacesData);
      } catch (error) {
        console.error("Error loading workspace info:", error);
      }

      router.push(sourcePage);
    } catch (error) {
      setLoginError("Invalid Google credentials");
      console.error("Google login error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("ee-token");
    localStorage.removeItem("ee-accessLevel");
    localStorage.removeItem("ee-username");
    setUser(null);
    setToken(null);
    setIsVerified(false);
    setCurrentWorkspace(null);
    setWorkspaces([]);
    router.push("/login");
  };

  const authValue: AuthContextType = {
    token,
    user,
    isVerified,
    isLoading,
    currentWorkspace,
    workspaces,
    login,
    loginError,
    loginGoogle,
    switchWorkspace,
    logout,
  };

  return (
    <AuthContext.Provider value={authValue}>{children}</AuthContext.Provider>
  );
};

export default AuthProvider;

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const useRequireVerified = () => {
  const { token, isVerified, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && token && !isVerified) {
      router.push("/verification-required");
    }
  }, [token, isVerified, isLoading, router]);

  return { token, isVerified, isLoading };
};
