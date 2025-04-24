import React from "react";

import { InformationCircleIcon } from "@heroicons/react/24/outline";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";

interface MethodCardProps {
  title: string;
  description: string;
  infoTitle: string;
  infoDescription: string;
  selected: boolean;
  disabled?: boolean;
  onClick: () => void;
}

export function MethodCard({
  title,
  description,
  infoTitle,
  infoDescription,
  selected,
  disabled = false,
  onClick,
}: MethodCardProps) {
  // Helper function to conditionally join classNames
  const classNames = (...classes: (string | boolean | undefined)[]) => {
    return classes.filter(Boolean).join(" ");
  };

  return (
    <div
      className={classNames(
        "relative flex flex-col p-4 rounded-lg border-2 transition-all h-full",
        selected
          ? "border-zinc-600 bg-zinc-50 shadow-md dark:bg-zinc-800 dark:border-zinc-700"
          : "border-zinc-200 bg-paper-50 dark:border-zinc-800 dark:bg-zinc-900",
        disabled
          ? "opacity-60 cursor-not-allowed"
          : "cursor-pointer hover:border-indigo-300 hover:bg-gray-50 dark:hover:bg-zinc-800/50"
      )}
      onClick={disabled ? undefined : onClick}
      aria-checked={selected}
      role="radio"
      aria-disabled={disabled}
      tabIndex={disabled ? -1 : 0}
      onKeyDown={(e) => {
        if ((e.key === "Enter" || e.key === " ") && !disabled) {
          e.preventDefault();
          onClick();
        }
      }}
    >
      <Dialog>
        <DialogTrigger asChild>
          <button
            className="absolute top-2 right-2 text-primary-foreground hover:text-indigo-600 dark:text-zinc-400 dark:hover:text-indigo-400"
            onClick={(e) => e.stopPropagation()}
            aria-label={`More information about ${title}`}
            disabled={disabled}
          >
            <InformationCircleIcon className="h-5 w-5" />
          </button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{infoTitle}</DialogTitle>
            <DialogDescription>{infoDescription}</DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>

      <div className="flex-1">
        <h3
          className={classNames(
            "text-lg font-medium mb-2 dark:text-zinc-200",
            disabled && "text-zinc-500"
          )}
        >
          {title}
          {disabled && <span className="ml-1 text-sm">[Coming soon]</span>}
        </h3>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">
          {description}
        </p>
      </div>
    </div>
  );
}
