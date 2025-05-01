"use client";
import * as React from "react";
import {
  ArrowLeftRightIcon,
  LayoutDashboardIcon,
  FlaskConicalIcon,
  Settings2,
  Building,
} from "lucide-react";
import { NavMain } from "@/components/nav-main";
import { NavRecentExperiments } from "@/components/nav-recent-experiments";
import { NavUser } from "@/components/nav-user";
import { WorkspaceSwitcher } from "@/components/workspace-switcher";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar";
import { useAuth } from "@/utils/auth";

const AppSidebar = React.memo(function AppSidebar({
  ...props
}: React.ComponentProps<typeof Sidebar>) {
  const { user, firstName, lastName } = useAuth();

  const navMain = [
    {
      title: "Experiments",
      url: "/experiments",
      icon: FlaskConicalIcon,
    },
    {
      title: "Dashboard",
      url: "#",
      icon: LayoutDashboardIcon,
    },
    {
      title: "Workspaces",
      url: "/workspaces",
      icon: Building,
    },
    {
      title: "Settings",
      url: "#",
      icon: Settings2,
    },
  ];

  const recentExperiments = [
    {
      name: "New onboarding flows",
      url: "#",
      icon: FlaskConicalIcon,
    },
    {
      name: "3 different voices",
      url: "#",
      icon: FlaskConicalIcon,
    },
    {
      name: "AI responses",
      url: "#",
      icon: FlaskConicalIcon,
    },
  ];

  const userDetails = {
    firstName: firstName || "?",
    lastName: lastName || "?",
    username: user || "loading",
  };

  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <WorkspaceSwitcher />
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={navMain} />
        <NavRecentExperiments experiments={recentExperiments} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={userDetails} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
});

export { AppSidebar };
