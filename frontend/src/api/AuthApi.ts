import type { CurrentUser, CurrentUserResponse } from "../types/CurrentUser";

const SAMPLE_USER: CurrentUser = {
  userId: "f81d4fae-7dec-41d0-a765-00a0c91e6bf6",
  username: "Test user",
  email: "user@test.com",
};

const GET_ME_ENDPOINT = "/api/users/me";

export const requestCurrentUser = async (): Promise<CurrentUser | null> => {
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
