export enum UserRoles {
  ADMIN = "ADMIN",
  EDITOR = "EDITOR",
  VIEWER = "VIEWER",
}

export interface Workspace {
  workspace_id: number;
  workspace_name: string;
  api_key_first_characters: string;
  api_key_updated_datetime_utc: string;
  api_daily_quota: number;
  content_quota: number;
  created_datetime_utc: string;
  updated_datetime_utc: string;
  is_default: boolean;
}

export interface WorkspaceCreate {
  workspace_name: string;
  api_daily_quota?: number;
  content_quota?: number;
}

export interface WorkspaceUpdate {
  workspace_name?: string;
  api_daily_quota?: number;
  content_quota?: number;
}

export interface WorkspaceKeyResponse {
  new_api_key: string;
  workspace_name: string;
}

export interface WorkspaceInvite {
  email: string;
  role: UserRoles;
  workspace_name: string;
}

export interface WorkspaceInviteResponse {
  message: string;
  email: string;
  workspace_name: string;
  user_exists: boolean;
}

export interface WorkspaceSwitch {
  workspace_name: string;
}
