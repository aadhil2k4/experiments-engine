"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/catalyst/button";
import { Input } from "@/components/catalyst/input";
import { useAuth } from "@/utils/auth";
import { apiCalls } from "@/utils/api";
import { useToast } from "@/hooks/use-toast";
import { useRouter } from "next/navigation";
import { useState } from "react";
import {
  Fieldset,
  Field,
  FieldGroup,
  Label,
  Description,
} from "@/components/catalyst/fieldset";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { BuildingOfficeIcon } from "@heroicons/react/20/solid";

const formSchema = z.object({
  workspace_name: z.string().min(3, {
    message: "Workspace name must be at least 3 characters",
  }),
});

type FormValues = z.infer<typeof formSchema>;

export default function CreateWorkspacePage() {
  const { token, switchWorkspace } = useAuth();
  const { toast } = useToast();
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      workspace_name: "",
    },
  });

  const onSubmit = async (data: FormValues) => {
    if (!token) {
      toast({
        title: "Error",
        description: "You must be logged in to create a workspace",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await apiCalls.createWorkspace(token, data);

      await switchWorkspace(response.workspace_name);

      toast({
        title: "Success",
        description: `Workspace "${response.workspace_name}" created and activated!`,
      });

      router.push("/workspace");
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to create workspace",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto py-10">
      <Card>
        <CardHeader className="pb-2 mb-4">
          <div className="flex items-center space-x-3">
            <BuildingOfficeIcon className="h-8 w-8 text-muted-foreground" />
            <div>
              <CardTitle className="text-2xl">Create new workspace</CardTitle>
              <CardDescription>
                Create a new workspace to organize your experiments and team members
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <Fieldset className="space-y-6">
              <FieldGroup>
                <Field>
                  <Label>Workspace Name</Label>
                  <Input
                    {...form.register("workspace_name")}
                    placeholder="Enter workspace name"
                  />
                  {form.formState.errors.workspace_name && (
                    <p className="text-red-500 text-sm mt-1">
                      {form.formState.errors.workspace_name.message}
                    </p>
                  )}
                  <Description>Choose a descriptive name for your new workspace.</Description>
                </Field>
              </FieldGroup>

              <div className="flex justify-end gap-4 mt-6">
                <Button
                  outline
                  type="button"
                  onClick={() => router.back()}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "Creating..." : "Create Workspace"}
                </Button>
              </div>
            </Fieldset>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
