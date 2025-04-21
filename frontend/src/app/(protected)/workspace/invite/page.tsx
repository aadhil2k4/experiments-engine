"use client";

import { useState } from "react";
import { useAuth } from "@/utils/auth";
import { apiCalls } from "@/utils/api";
import { useToast } from "@/hooks/use-toast";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Button } from "@/components/catalyst/button";
import { Heading } from "@/components/catalyst/heading";
import { Input } from "@/components/catalyst/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Fieldset,
  Field,
  FieldGroup,
  Label,
  Description,
} from "@/components/catalyst/fieldset";
import { Radio, RadioField, RadioGroup } from "@/components/catalyst/radio";
import { Badge } from "@/components/ui/badge";
import { EnvelopeIcon, UserPlusIcon } from "@heroicons/react/20/solid";

const inviteSchema = z.object({
  email: z.string().email({
    message: "Please enter a valid email address",
  }),
  role: z.enum(["ADMIN", "EDITOR", "VIEWER"], {
    required_error: "Please select a role",
  }),
});

type InviteFormValues = z.infer<typeof inviteSchema>;

export default function InviteUsersPage() {
  const { token, currentWorkspace } = useAuth();
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [invitedUsers, setInvitedUsers] = useState<{ email: string; role: string; exists: boolean }[]>([]);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
    setValue,
    watch,
  } = useForm<InviteFormValues>({
    resolver: zodResolver(inviteSchema),
    defaultValues: {
      email: "",
      role: "VIEWER",
    },
  });

  const roleValue = watch("role");

  const onSubmit = async (data: InviteFormValues) => {
    if (!token || !currentWorkspace) {
      toast({
        title: "Error",
        description: "You must be logged in and have a workspace selected",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await apiCalls.inviteUserToWorkspace(token, {
        email: data.email,
        role: data.role,
        workspace_name: currentWorkspace.workspace_name,
      });

      // Add to invited users list
      setInvitedUsers([
        ...invitedUsers,
        {
          email: data.email,
          role: data.role,
          exists: response.user_exists,
        },
      ]);

      // Reset form
      reset();

      toast({
        title: "Success",
        description: `Invitation sent to ${data.email}`,
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to send invitation",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto py-10">
      <div className="flex items-center justify-between mb-6">
        <Heading>Invite Team Members</Heading>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Send Invitation</CardTitle>
              <CardDescription>
                Invite users to join your workspace: {currentWorkspace?.workspace_name}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                <Fieldset>
                  <FieldGroup>
                    <Field>
                      <Label>Email Address</Label>
                      <Input
                        {...register("email")}
                        placeholder="colleague@example.com"
                        type="email"
                      />
                      {errors.email && (
                        <p className="text-red-500 text-sm mt-1">
                          {errors.email.message}
                        </p>
                      )}
                      <Description>Enter the email address of the person you want to invite.</Description>
                    </Field>
                  </FieldGroup>

                  <FieldGroup className="mt-6">
                    <Label>Permission Level</Label>
                    <RadioGroup
                      name="role"
                      value={roleValue}
                      onChange={(value) => setValue("role", value as "ADMIN" | "VIEWER")}
                    >
                      <RadioField>
                        <Radio id="admin" value="ADMIN" />
                        <Label htmlFor="admin">Administrator</Label>
                        <Description>
                          Can manage workspace settings, invite members, and has full access to all resources.
                        </Description>
                      </RadioField>
                      <RadioField>
                        <Radio id="viewer" value="VIEWER" />
                        <Label htmlFor="viewer">Viewer</Label>
                        <Description>
                          Can only view resources, but cannot edit them or change any settings.
                        </Description>
                      </RadioField>
                    </RadioGroup>
                    {errors.role && (
                      <p className="text-red-500 text-sm mt-1">
                        {errors.role.message}
                      </p>
                    )}
                  </FieldGroup>
                </Fieldset>

                <div className="flex justify-end">
                  <Button
                    type="submit"
                    disabled={isSubmitting}
                  >
                    <UserPlusIcon className="h-5 w-5 mr-2" />
                    {isSubmitting ? "Sending..." : "Send Invitation"}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
