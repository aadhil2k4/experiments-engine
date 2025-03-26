import api from "@/utils/api";
import { Message } from "./types";

const getMessages = async ({ token }: { token: string | null }) => {
  const response = await api.get("/messages/", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data as Message[];
};

const patchMessageReadStatus = async ({
  token,
  message_ids,
  is_unread,
}: {
  token: string | null;
  message_ids: number[];
  is_unread: boolean;
}) => {
  const response = await api.patch(
    "/messages/",
    {
      message_ids,
      is_unread,
    },
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return response.data as Message[];
};

const deleteMessages = async ({
  token,
  message_ids,
}: {
  token: string | null;
  message_ids: number[];
}) => {
  const response = await api.delete("/messages/", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    data: message_ids,
  });
  return response.data as Message[];
};
export { getMessages, patchMessageReadStatus, deleteMessages };
