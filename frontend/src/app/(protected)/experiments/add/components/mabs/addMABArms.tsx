import {
  useExperimentStore,
  isMABExperimentStateNormal,
} from "../../../store/useExperimentStore";
import {
  Field,
  FieldGroup,
  Fieldset,
  Label,
} from "@/components/catalyst/fieldset";
import { Button } from "@/components/catalyst/button";
import { Input } from "@/components/catalyst/input";
import { Textarea } from "@/components/catalyst/textarea";
import {
  NewMABArmNormal,
  StepComponentProps,
  MABArmBeta,
  MABArmNormal,
} from "../../../types";
import { PlusIcon } from "@heroicons/react/16/solid";
import { DividerWithTitle } from "@/components/Dividers";
import { TrashIcon } from "@heroicons/react/16/solid";
import { Heading } from "@/components/catalyst/heading";
import { useCallback, useEffect, useState, useMemo } from "react";

export default function AddMABArms({ onValidate }: StepComponentProps) {
  const { experimentState, updateArm, addArm, removeArm } =
    useExperimentStore();
  console.log("experimentState", experimentState);

  const [inputValues, setInputValues] = useState<Record<string, string>>({});

  const baseArmDesc = useMemo(
    () => ({
      name: "",
      description: "",
    }),
    []
  );

  const additionalArmErrors = useMemo(
    () =>
      experimentState.priorType === "beta"
        ? { alpha: "", beta: "" }
        : { mu: "", sigma: "" },
    [experimentState]
  );

  const [errors, setErrors] = useState(() => {
    return experimentState.arms.map(() => {
      return { ...baseArmDesc, ...additionalArmErrors };
    });
  });

  const validateForm = useCallback(() => {
    let isValid = true;
    const newErrors = experimentState.arms.map(() => ({
      ...baseArmDesc,
      ...additionalArmErrors,
    }));

    experimentState.arms.forEach((arm, index) => {
      if (!arm.name.trim()) {
        newErrors[index].name = "Arm name is required";
        isValid = false;
      }

      if (!arm.description.trim()) {
        newErrors[index].description = "Description is required";
        isValid = false;
      }

      if (experimentState.priorType === "beta") {
        if ("alpha" in arm) {
          if (!arm.alpha) {
            newErrors[index].alpha = "Alpha prior is required";
            isValid = false;
          }
          if (arm.alpha <= 0) {
            newErrors[index].alpha = "Alpha prior should be greater than 0";
            isValid = false;
          }
        }

        if ("beta" in arm) {
          if (!arm.beta) {
            newErrors[index].beta = "Beta prior is required";
            isValid = false;
          }

          if (arm.beta <= 0) {
            newErrors[index].beta = "Beta prior should be greater than 0";
            isValid = false;
          }
        }
      } else if (experimentState.priorType === "normal") {
        if ("mu" in arm && typeof arm.mu !== "number") {
          newErrors[index].mu = "Mean value is required";
          isValid = false;
        }

        if ("sigma" in arm) {
          if (!arm.sigma) {
            newErrors[index].sigma = "Std. deviation is required";
            isValid = false;
          }

          if (arm.sigma <= 0) {
            newErrors[index].sigma = "Std deviation should be greater than 0";
            isValid = false;
          }
        }
      }
    });
    return { isValid, newErrors };
  }, [experimentState, baseArmDesc, additionalArmErrors]);

  useEffect(() => {
    const { isValid, newErrors } = validateForm();
    if (JSON.stringify(newErrors) !== JSON.stringify(errors)) {
      setErrors(newErrors);
      onValidate({
        isValid,
        errors: newErrors.map((error) =>
          Object.fromEntries(
            Object.entries(error).map(([key, value]) => [key, value ?? ""])
          )
        ),
      });
    }
  }, [validateForm, onValidate, errors]);

  useEffect(() => {
    const newInputValues: Record<string, string> = {};

    if (isMABExperimentStateNormal(experimentState)) {
      experimentState.arms.forEach((arm, index) => {
        newInputValues[`${index}-mu`] = (
          (arm as MABArmNormal).mu || 0
        ).toString();
      });
    }
    setInputValues(newInputValues);
  }, [experimentState]);

  const handleNumericChange = (index: number, value: string) => {
    // Update the local input state for a smooth typing experience
    setInputValues((prev) => ({
      ...prev,
      [`${index}-mu`]: value,
    }));

    if (value !== "" && value !== "-") {
      const numValue = Number.parseFloat(value);
      if (!isNaN(numValue)) {
        updateArm(index, { mu: numValue });
      }
    }
  };

  return (
    <div>
      <div className="flex w-full flex-wrap items-end justify-between gap-4 border-b border-zinc-950/10 pb-6 dark:border-white/10">
        <Heading>Add MAB Arms</Heading>
        <div className="flex gap-4">
          <Button className="mt-4" onClick={addArm}>
            <PlusIcon className="w-4 h-4 mr-2" />
            Add Arm
          </Button>
          <Button
            className="mt-4 mx-4"
            disabled={experimentState.arms.length <= 2}
            outline
            onClick={() => {
              removeArm(experimentState.arms.length - 1);
            }}
          >
            <TrashIcon className="w-4 h-4 mr-2" />
            Delete Arm
          </Button>
        </div>
      </div>
      <Fieldset aria-label="Add MAB Arms">
        {experimentState.arms.map((arm, index) => (
          <div key={index}>
            <DividerWithTitle title={`Arm ${index + 1}`} />
            <FieldGroup
              key={index}
              className="md:flex md:flex-row md:space-x-8 md:space-y-0 items-start"
            >
              <div className="basis-1/2">
                <Field className="flex flex-col mb-4">
                  <div className="flex flex-row">
                    <Label className="basis-1/4 mt-3 font-medium">Name</Label>
                    <div className="basis-3/4 flex flex-col">
                      <Input
                        name={`arm-${index + 1}-name`}
                        placeholder="Give the arm a searchable name"
                        value={arm.name || ""}
                        onChange={(e) =>
                          updateArm(index, { name: e.target.value })
                        }
                      />
                      {errors[index]?.name ? (
                        <p className="text-red-500 text-xs mt-1">
                          {errors[index].name}
                        </p>
                      ) : (
                        <p className="text-red-500 text-xs mt-1">&nbsp;</p>
                      )}
                    </div>
                  </div>
                </Field>
                <Field className="flex flex-col">
                  <div className="flex flex-row">
                    <Label className="basis-1/4 mt-3 font-medium">
                      Description
                    </Label>
                    <div className="basis-3/4 flex flex-col">
                      <Textarea
                        name={`arm-${index + 1}-description`}
                        placeholder="Describe the arm"
                        value={arm.description || ""}
                        onChange={(e) =>
                          updateArm(index, { description: e.target.value })
                        }
                      />
                      {errors[index]?.description ? (
                        <p className="text-red-500 text-xs mt-1">
                          {errors[index].description}
                        </p>
                      ) : (
                        <p className="text-red-500 text-xs mt-1">&nbsp;</p>
                      )}
                    </div>
                  </div>
                </Field>
              </div>
              {experimentState.priorType === "beta" && (
                <div className="basis-1/2 grow">
                  <Field className="flex flex-col mb-4">
                    <div className="flex flex-row">
                      <Label
                        className="basis-1/4 mt-3 font-medium"
                        htmlFor="alpha"
                      >
                        Alpha prior
                      </Label>
                      <div className="basis-3/4 flex flex-col">
                        <Input
                          id={`arm-${index + 1}-alpha`}
                          name={`arm-${index + 1}-alpha`}
                          placeholder="Enter an integer as the prior for the alpha parameter"
                          value={(arm as MABArmBeta).alpha || ""}
                          onChange={(e) => {
                            updateArm(index, {
                              alpha: parseInt(e.target.value),
                            });
                          }}
                        />
                        {errors[index]?.alpha ? (
                          <p className="text-red-500 text-xs mt-1">
                            {errors[index].alpha}
                          </p>
                        ) : (
                          <p className="text-red-500 text-xs mt-1">&nbsp;</p>
                        )}
                      </div>
                    </div>
                  </Field>
                  <Field className="flex flex-col">
                    <div className="flex flex-row">
                      <Label
                        className="basis-1/4 mt-3 font-medium"
                        htmlFor="beta"
                      >
                        Beta prior
                      </Label>
                      <div className="basis-3/4 flex flex-col">
                        <Input
                          id={`arm-${index + 1}-beta`}
                          name={`arm-${index + 1}-beta`}
                          placeholder="Enter an integer as the prior for the beta parameter"
                          value={(arm as MABArmBeta).beta || ""}
                          onChange={(e) => {
                            updateArm(index, {
                              beta: parseInt(e.target.value),
                            });
                          }}
                        />
                        {errors[index]?.beta ? (
                          <p className="text-red-500 text-xs mt-1">
                            {errors[index].beta}
                          </p>
                        ) : (
                          <p className="text-red-500 text-xs mt-1">&nbsp;</p>
                        )}
                      </div>
                    </div>
                  </Field>
                </div>
              )}
              {experimentState.priorType === "normal" && (
                <div className="basis-1/2 grow">
                  <Field className="flex flex-col mb-4">
                    <div className="flex flex-row">
                      <Label
                        className="basis-1/4 mt-3 font-medium"
                        htmlFor="mu"
                      >
                        Mean prior
                      </Label>
                      <div className="basis-3/4 flex flex-col">
                        <Input
                          id={`arm-${index + 1}-mu`}
                          name={`arm-${index + 1}-mu`}
                          type="number"
                          placeholder="Enter a float as mean for the prior"
                          defaultValue={0}
                          value={
                            inputValues[`${index}-mu`] ??
                            (arm as MABArmNormal).mu?.toString()
                          }
                          onChange={(e) => {
                            handleNumericChange(index, e.target.value);
                          }}
                        />
                        {errors[index]?.mu ? (
                          <p className="text-red-500 text-xs mt-1">
                            {errors[index].mu}
                          </p>
                        ) : (
                          <p className="text-red-500 text-xs mt-1">&nbsp;</p>
                        )}
                      </div>
                    </div>
                  </Field>
                  <Field className="flex flex-col">
                    <div className="flex flex-row">
                      <Label
                        className="basis-1/4 mt-3 font-medium"
                        htmlFor="sigma"
                      >
                        Standard deviation
                      </Label>
                      <div className="basis-3/4 flex flex-col">
                        <Input
                          id={`arm-${index + 1}-sigma`}
                          name={`arm-${index + 1}-sigma`}
                          type="number"
                          defaultValue={1}
                          placeholder="Enter a float as standard deviation for the prior"
                          value={(arm as NewMABArmNormal).sigma || ""}
                          onChange={(e) => {
                            updateArm(index, { sigma: Number(e.target.value) });
                          }}
                        />
                        {errors[index]?.sigma ? (
                          <p className="text-red-500 text-xs mt-1">
                            {errors[index].sigma}
                          </p>
                        ) : (
                          <p className="text-red-500 text-xs mt-1">&nbsp;</p>
                        )}
                      </div>
                    </div>
                  </Field>
                </div>
              )}
            </FieldGroup>
          </div>
        ))}
      </Fieldset>
    </div>
  );
}
