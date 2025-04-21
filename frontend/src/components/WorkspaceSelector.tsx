"use client";

import React, { useState } from "react";
import { useAuth } from "@/utils/auth";
import { Button } from "@/components/catalyst/button";
import {
  Dialog,
  DialogActions,
  DialogBody,
  DialogDescription,
  DialogTitle,
} from "@/components/catalyst/dialog";
import { BuildingOfficeIcon, ChevronUpDownIcon, PlusIcon } from "@heroicons/react/20/solid";
import {
  DropdownItem,
  DropdownLabel,
  DropdownMenu,
  DropdownButton,
  DropdownDivider,
  Dropdown,
} from "@/components/catalyst/dropdown";
import { useToast } from "@/hooks/use-toast";
import { useRouter } from "next/navigation";

export default function WorkspaceSelector() {
  const { currentWorkspace, workspaces, switchWorkspace, isLoading } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const { toast } = useToast();
  const router = useRouter();

  const handleSwitchWorkspace = async (workspaceName: string) => {
    try {
      await switchWorkspace(workspaceName);
      toast({
        title: "Workspace Changed",
        description: `Switched to workspace: ${workspaceName}`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to switch workspace",
        variant: "destructive",
      });
    }
  };

  const handleCreateWorkspace = () => {
    router.push("/workspace/create");
  };

  if (isLoading || !currentWorkspace) {
    return (
      <Button
        outline
        className="w-full text-left justify-between"
        disabled={true}
      >
        <span className="flex items-center space-x-2">
          <BuildingOfficeIcon className="h-5 w-5" />
          <span>Loading...</span>
        </span>
        <ChevronUpDownIcon className="h-5 w-5" />
      </Button>
    );
  }

  return (
    <div className="px-1 py-2">
      <Dropdown>
        <DropdownButton
          as={Button}
          outline
          className="w-full text-left justify-between"
        >
          <span className="flex items-center space-x-2 truncate">
            <BuildingOfficeIcon className="h-5 w-5 shrink-0" />
            <span className="truncate">{currentWorkspace.workspace_name}</span>
          </span>
          <ChevronUpDownIcon className="h-5 w-5 shrink-0" />
        </DropdownButton>

        <DropdownMenu anchor="bottom start">
          {workspaces.map((workspace) => (
            <DropdownItem
              key={workspace.workspace_id}
              onClick={() => handleSwitchWorkspace(workspace.workspace_name)}
            >
              <BuildingOfficeIcon />
              <DropdownLabel>{workspace.workspace_name}</DropdownLabel>
            </DropdownItem>
          ))}
          
          <DropdownDivider />
          
          <DropdownItem onClick={handleCreateWorkspace}>
            <PlusIcon />
            <DropdownLabel>Create New Workspace</DropdownLabel>
          </DropdownItem>
        </DropdownMenu>
      </Dropdown>

      <Dialog open={isOpen} onClose={() => setIsOpen(false)}>
        <DialogTitle>Switch Workspace</DialogTitle>
        <DialogDescription>
          Select a workspace to switch to
        </DialogDescription>
        <DialogBody>
          <div className="space-y-4">
            {workspaces.map((workspace) => (
              <div
                key={workspace.workspace_id}
                className={`p-4 border rounded-lg cursor-pointer ${
                  workspace.workspace_id === currentWorkspace.workspace_id
                    ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                    : "border-gray-200 hover:border-blue-300 dark:border-gray-700"
                }`}
                onClick={() => {
                  handleSwitchWorkspace(workspace.workspace_name);
                  setIsOpen(false);
                }}
              >
                <div className="font-medium">{workspace.workspace_name}</div>
                {workspace.workspace_id === currentWorkspace.workspace_id && (
                  <div className="text-xs text-blue-500 mt-1">Current</div>
                )}
              </div>
            ))}
          </div>
        </DialogBody>
        <DialogActions>
          <Button outline onClick={() => setIsOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleCreateWorkspace}>
            <PlusIcon className="h-5 w-5 mr-1" />
            Create New
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}