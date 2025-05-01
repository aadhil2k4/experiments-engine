export type WorkspaceUser = {
  user_id: number;
  username: string;
  first_name: string;
  last_name: string;
  role: string;
  is_default_workspace: boolean;
  created_datetime_utc: string;
};

export type Workspace = {
  workspace_id: number;
  workspace_name: string;
  api_key_first_characters: string;
  api_daily_quota: number;
  content_quota: number;
  created_datetime_utc: string;
  updated_datetime_utc: string;
  api_key_updated_datetime_utc: string;
  is_default: boolean;
};

