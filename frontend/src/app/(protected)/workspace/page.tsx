"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/utils/auth";
import { Heading } from "@/components/catalyst/heading";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Plus, Users, Settings, Key } from "lucide-react";
import { Button } from "@/components/catalyst/button";

export default function WorkspacePage() {
  const { currentWorkspace } = useAuth();
  const router = useRouter();

  if (!currentWorkspace) {
    return (
      <div className="container mx-auto py-10">
        <Card>
          <CardHeader>
            <CardDescription>
              Something went wrong. Please try again later.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }
  console.log("Current Workspace:", currentWorkspace);

  return (
    <div className="container mx-auto">
      <div className="flex items-center justify-between mb-6">
        <Heading>{currentWorkspace.workspace_name}</Heading>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <Card>
          <CardHeader>
            <CardTitle>Workspace Information</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="space-y-4">
              <div className="flex justify-between">
                <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Name:</dt>
                <dd className="text-sm text-gray-900 dark:text-white">{currentWorkspace.workspace_name}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">API Quota:</dt>
                <dd className="text-sm text-gray-900 dark:text-white">{currentWorkspace.api_daily_quota.toLocaleString()} calls/day</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Experiment Quota:</dt>
                <dd className="text-sm text-gray-900 dark:text-white">{currentWorkspace.content_quota.toLocaleString()} experiments</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Created:</dt>
                <dd className="text-sm text-gray-900 dark:text-white">
                  {new Date(currentWorkspace.created_datetime_utc).toLocaleDateString()}
                </dd>
              </div>
            </dl>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>API Key</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between p-4 border flex-wrap gap-4 rounded-lg bg-muted">
              <div className="flex items-center gap-2">
                <Key className="w-4 h-4 text-muted-foreground" />
                <span className="font-mono">
                  {currentWorkspace.api_key_first_characters}
                  {"•".repeat(27)}
                </span>
              </div>
              <Button onClick={() => router.push('/integration')}>
                Manage API Keys
              </Button>
            </div>
            <p className="text-sm text-muted-foreground mt-4">
              Use this API key to authenticate your API requests. Keep it secret and secure.
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => router.push('/workspace/invite')}>
          <CardHeader className="flex flex-row items-start space-y-0">
            <div className="flex-1">
              <CardTitle>Invite Team Members</CardTitle>
              <CardDescription>
                Invite colleagues to join your workspace
              </CardDescription>
            </div>
            <Users className="h-6 w-6 text-muted-foreground" />
          </CardHeader>
        </Card>

        <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => router.push('/workspace/create')}>
          <CardHeader className="flex flex-row items-start space-y-0">
            <div className="flex-1">
              <CardTitle>Create New Workspace</CardTitle>
              <CardDescription>
                Create a new workspace for different projects
              </CardDescription>
            </div>
            <Plus className="h-6 w-6 text-muted-foreground" />
          </CardHeader>
        </Card>
      </div>
    </div>
  );
}
