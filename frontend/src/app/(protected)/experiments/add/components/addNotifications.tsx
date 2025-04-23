import { useExperimentStore } from "../../store/useExperimentStore";
import { Heading } from "@/components/catalyst/heading";
import {
  Checkbox,
  CheckboxField,
  CheckboxGroup,
} from "@/components/catalyst/checkbox";
import { Description, Fieldset, Label } from "@/components/catalyst/fieldset";
import { Input } from "@/components/ui/input";
import { StepComponentProps } from "../../types";
import { useCallback, useEffect, useState } from "react";

export default function AddNotifications({ onValidate }: StepComponentProps) {
  const { experimentState, updateNotifications } = useExperimentStore();

  const inputClasses = `
    w-16 mx-1 px-1 py-0 h-6 inline-block font-bold rounded-none
    border-0 border-b-4 border-zinc-200 text-center
    focus:border-primary focus:border-0 focus:border-b-2 focus:ring-0 focus:ring-offset-0
    shadow-none appearance-none [&::-webkit-outer-spin-button]:appearance-none
    [&::-webkit-inner-spin-button]:appearance-none
    [-moz-appearance:textfield]
  `;

  const [errors, setErrors] = useState({
    numberOfTrials: "",
    daysElapsed: "",
    percentBetterThreshold: "",
  });

  const validateForm = useCallback(() => {
    let isValid = true;
    const newErrors = {
      numberOfTrials: "",
      daysElapsed: "",
      percentBetterThreshold: "",
    };

    if (
      experimentState.notifications.onTrialCompletion &&
      (!experimentState.notifications.numberOfTrials ||
        experimentState.notifications.numberOfTrials < 0)
    ) {
      newErrors.numberOfTrials = "Number of trials should be greater than 0";
      isValid = false;
    }
    if (
      experimentState.notifications.onDaysElapsed &&
      (!experimentState.notifications.daysElapsed ||
        experimentState.notifications.daysElapsed < 0)
    ) {
      newErrors.daysElapsed = "Days elapsed should be greater than 0";
      isValid = false;
    }
    if (
      experimentState.notifications.onPercentBetter &&
      (!experimentState.notifications.percentBetterThreshold ||
        experimentState.notifications.percentBetterThreshold < 0)
    ) {
      newErrors.percentBetterThreshold = "Threshold should be greater than 0";
      isValid = false;
    }
    return { isValid, newErrors };
  }, [experimentState]);

  useEffect(() => {
    const { isValid, newErrors } = validateForm();
    if (JSON.stringify(newErrors) !== JSON.stringify(errors)) {
      setErrors(newErrors);
      onValidate({ isValid, errors: newErrors });
    }
  }, [validateForm, onValidate, errors]);

  return (
    <div>
      <div className="pt-5 flex w-full flex-wrap items-end justify-between gap-4 border-b border-zinc-950/10 pb-6 dark:border-white/10">
        <Heading>Select notifications</Heading>
      </div>
      <Fieldset aria-label="select notifications" className="pt-6">
        <CheckboxGroup>
          <CheckboxField className="flex flex-row">
            <Checkbox
              name="discoverability"
              defaultChecked={
                experimentState.notifications.onTrialCompletion || false
              }
              onChange={(e) =>
                updateNotifications({
                  ...experimentState.notifications,
                  onTrialCompletion: e,
                })
              }
            />
            <Label>
              After
              <Input
                type="number"
                value={experimentState.notifications.numberOfTrials}
                onChange={(e) => {
                  updateNotifications({
                    ...experimentState.notifications,
                    numberOfTrials: Number(e.target.value),
                  });
                }}
                className={`${inputClasses} ${
                  errors.numberOfTrials ? "border-red-500" : ""
                }`}
                onClick={(e) => e.stopPropagation()}
              />
              {" trials"}
            </Label>
            <Description>
              {errors.numberOfTrials ? (
                <span className="text-red-500">{errors.numberOfTrials}</span>
              ) : (
                <span>
                  Notify me when{" "}
                  <b>{experimentState.notifications.numberOfTrials}</b> number
                  of trials have been run
                </span>
              )}
            </Description>
          </CheckboxField>
          <CheckboxField>
            <Checkbox
              name="discoverability"
              value="time"
              defaultChecked={
                experimentState.notifications.onDaysElapsed || false
              }
              onChange={(e) =>
                updateNotifications({
                  ...experimentState.notifications,
                  onDaysElapsed: e,
                })
              }
            />
            <Label>
              After
              <Input
                type="number"
                value={experimentState.notifications.daysElapsed}
                onChange={(e) =>
                  updateNotifications({
                    ...experimentState.notifications,
                    daysElapsed: Number(e.target.value),
                  })
                }
                className={`${inputClasses} ${
                  errors.daysElapsed ? "border-red-500" : ""
                }`}
                onClick={(e) => e.stopPropagation()}
              />
              {" days"}
            </Label>
            <Description>
              {errors.daysElapsed ? (
                <span className="text-red-500">{errors.daysElapsed}</span>
              ) : (
                <span>
                  Notify me when{" "}
                  <b>{experimentState.notifications.daysElapsed}</b> days have
                  passed since the experiment started
                </span>
              )}
            </Description>
          </CheckboxField>
          <CheckboxField>
            <Checkbox
              name="discoverability"
              value="event"
              disabled={true}
              defaultChecked={
                experimentState.notifications.onPercentBetter || false
              }
              onChange={(e) =>
                updateNotifications({
                  ...experimentState.notifications,
                  onPercentBetter: e,
                })
              }
            />
            <Label>
              <span className="text-gray-400">
                [Coming soon] If an arm is superior by
                <Input
                  type="number"
                  value={experimentState.notifications.percentBetterThreshold}
                  onChange={(e) =>
                    updateNotifications({
                      ...experimentState.notifications,
                      percentBetterThreshold: Number(e.target.value),
                    })
                  }
                  className={`${inputClasses} ${
                    errors.percentBetterThreshold ? "border-red-500" : ""
                  }`}
                  onClick={(e) => e.stopPropagation()}
                  disabled={true}
                />
                {"%"}
              </span>
            </Label>
            <Description>
              {errors.percentBetterThreshold ? (
                <span className="text-red-500">
                  {errors.percentBetterThreshold}
                </span>
              ) : (
                <span>
                  Notify me if an arm is{" "}
                  <b>{experimentState.notifications.percentBetterThreshold}</b>%
                  better than the other arms
                </span>
              )}
            </Description>
          </CheckboxField>
        </CheckboxGroup>
      </Fieldset>
    </div>
  );
}
