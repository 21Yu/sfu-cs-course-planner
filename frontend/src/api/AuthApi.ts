import type { LoginRequest, SignUpRequest } from "#types/Auth";
import type { CurrentUser, CurrentUserResponse } from "#types/CurrentUser";

// Hardcoded sample user
const SAMPLE_USER: CurrentUser = {
  userId: "f81d4fae-7dec-41d0-a765-00a0c91e6bf6",
  username: "Test user",
  email: "user@test.com",
};

// Assumed endpoints
const GET_ME_ENDPOINT = "/api/users/me";
const LOGIN_ENDPOINT = "/api/users/login";
const LOGOUT_ENDPOINT = "/api/users/logout";
const SIGNUP_ENDPOINT = "/api/users/signup";

const sendAuthenticationRequest = async (
  endpoint: string,
  requestBody: SignUpRequest | LoginRequest,
  fallbackErrorMessage: string,
) => {
  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify(requestBody),
  });
  if (!response.ok) {
    throw new Error(fallbackErrorMessage);
  }
  const data = await response.json();
  return data.user;
};

export const requestCurrentUser = async (): Promise<CurrentUser | null> => {
  const user: CurrentUser = SAMPLE_USER;
  return null; // For logged-out user pages
  return user; // For logged-in user pages

  // TODO: Test and modify function for actual endpoint once it is implemented
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

export const loginUser = async (
  loginRequest: LoginRequest,
): Promise<CurrentUser | null> => {
  return sendAuthenticationRequest(
    LOGIN_ENDPOINT,
    loginRequest,
    "Failed to login",
  );
};

export const logoutUser = async (): Promise<void> => {
  const response = await fetch(LOGOUT_ENDPOINT, {
    method: "POST",
    credentials: "include",
  });
  if (!response.ok) {
    throw new Error("Failed to logout");
  }
};

export const signUpUser = async (
  signUpRequest: SignUpRequest,
): Promise<CurrentUser | null> => {
  return sendAuthenticationRequest(
    SIGNUP_ENDPOINT,
    signUpRequest,
    "Failed to signup",
  );
};
