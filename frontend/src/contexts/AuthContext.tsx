import {
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { createContext } from "react";
import type { CurrentUser, CurrentUserResponse } from "../types/currentUser";

interface AuthContextType {
  currentUser: CurrentUser | null;
  isLoading: boolean;
  refreshCurrentUser: () => Promise<void>;
  clearCurrentUser: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const SAMPLE_USER: CurrentUser = {
  userId: "f81d4fae-7dec-41d0-a765-00a0c91e6bf6",
  username: "Test user",
  email: "user@test.com",
};
const GET_ME_ENDPOINT = "/api/users/me";
const requestCurrentUser = async (): Promise<CurrentUser | null> => {
  const user: CurrentUser = SAMPLE_USER;
  return user;

  const response = await fetch(GET_ME_ENDPOINT, {
    credentials: "include",
  });
  if (response.status === 401) {
    return null;
  }
  if (!response.ok) {
    throw new Error(`Error with ${GET_ME_ENDPOINT}, requesting current user`);
  }
  const data: CurrentUserResponse = await response.json();
  return data.user;
};

export const AuthContextProvider = ({ children }: { children: ReactNode }) => {
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const refreshCurrentUser = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    try {
      const user = await requestCurrentUser();
      setCurrentUser(user);
    } catch (error) {
      setCurrentUser(null);
      console.error(`Failed to load current user: ${error}`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearCurrentUser = useCallback(() => {
    setCurrentUser(null);
  }, []);

  useEffect(() => {
    const loadInitialUser = async (): Promise<void> => {
      await refreshCurrentUser();
    };
    loadInitialUser();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        isLoading,
        refreshCurrentUser,
        clearCurrentUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("Error with useAuth hook.");
  }
  return context;
};
