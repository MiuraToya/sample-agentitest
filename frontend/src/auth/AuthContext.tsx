import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react";
import {
  CognitoUserPool,
  CognitoUser,
  AuthenticationDetails,
  type CognitoUserSession,
} from "amazon-cognito-identity-js";

const userPool = new CognitoUserPool({
  UserPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID,
  ClientId: import.meta.env.VITE_COGNITO_CLIENT_ID,
});

type AuthState =
  | { status: "loading" }
  | { status: "unauthenticated" }
  | { status: "authenticated"; idToken: string; email: string };

type AuthContextType = {
  auth: AuthState;
  signUp: (email: string, password: string) => Promise<void>;
  confirmSignUp: (email: string, code: string) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => void;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [auth, setAuth] = useState<AuthState>({ status: "loading" });

  useEffect(() => {
    const user = userPool.getCurrentUser();
    if (!user) {
      setAuth({ status: "unauthenticated" });
      return;
    }
    user.getSession((err: Error | null, session: CognitoUserSession | null) => {
      if (err || !session?.isValid()) {
        setAuth({ status: "unauthenticated" });
        return;
      }
      setAuth({
        status: "authenticated",
        idToken: session.getIdToken().getJwtToken(),
        email: session.getIdToken().payload.email,
      });
    });
  }, []);

  const signUp = (email: string, password: string): Promise<void> =>
    new Promise((resolve, reject) => {
      userPool.signUp(email, password, [], [], (err) => {
        if (err) return reject(err);
        resolve();
      });
    });

  const confirmSignUp = (email: string, code: string): Promise<void> =>
    new Promise((resolve, reject) => {
      const user = new CognitoUser({ Username: email, Pool: userPool });
      user.confirmRegistration(code, true, (err) => {
        if (err) return reject(err);
        resolve();
      });
    });

  const signIn = (email: string, password: string): Promise<void> =>
    new Promise((resolve, reject) => {
      const user = new CognitoUser({ Username: email, Pool: userPool });
      user.authenticateUser(
        new AuthenticationDetails({ Username: email, Password: password }),
        {
          onSuccess: (session) => {
            setAuth({
              status: "authenticated",
              idToken: session.getIdToken().getJwtToken(),
              email: session.getIdToken().payload.email,
            });
            resolve();
          },
          onFailure: (err) => reject(err),
        }
      );
    });

  const signOut = () => {
    const user = userPool.getCurrentUser();
    user?.signOut();
    setAuth({ status: "unauthenticated" });
  };

  return (
    <AuthContext.Provider value={{ auth, signUp, confirmSignUp, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
