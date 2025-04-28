import { useExperimentStore } from "../../../store/useExperimentStore";
import { useCallback, useState, useEffect } from "react";
import { Radio, RadioField, RadioGroup } from "@/components/catalyst/radio";
import { Fieldset, Label, Description } from "@/components/catalyst/fieldset";
import type { RewardType, StepComponentProps } from "../../../types";
import { Heading } from "@/components/catalyst/heading";
import { DividerWithTitle } from "@/components/Dividers";

export default function CMABPriorRewardSelection({
  onValidate,
}: StepComponentProps) {
  const { experimentState, updateRewardType } = useExperimentStore();
  const [errors, setErrors] = useState({
    prior_type: "",
    reward_type: "",
  });

  const validateForm = useCallback(() => {
    let isValid = true;
    const newErrors = {
      prior_type: "",
      reward_type: "",
    };

    // Prior type is fixed as "normal" for CMAB, so we don't need to validate it
    if (!experimentState.reward_type) {
      newErrors.reward_type = "Please select a reward type";
      isValid = false;
    }

    return { isValid, newErrors };
  }, [experimentState.reward_type]);

  useEffect(() => {
    const { isValid, newErrors } = validateForm();
    if (JSON.stringify(newErrors) !== JSON.stringify(errors)) {
      setErrors(newErrors);
      onValidate({ isValid, errors: newErrors });
    }
  }, [validateForm, onValidate, errors]);

  useEffect(() => {
    const { isValid, newErrors } = validateForm();
    setErrors(newErrors);
    onValidate({ isValid, errors: newErrors });
  }, []);

  return (
    <div>
      <div className="pt-5 flex w-full flex-wrap items-end justify-between gap-4 border-b border-zinc-950/10 pb-6 dark:border-white/10">
        <Heading>Configure CMAB Parameters</Heading>
      </div>
      <Fieldset aria-label="CMAB Parameters" className="pt-6">
        <DividerWithTitle title="Prior Type" />
        <RadioGroup
          name="priorType"
          defaultValue="normal"
          value={experimentState.prior_type}
        >
          <div className="mb-4" />
          <Label>Select prior type for the experiment</Label>
          <RadioField>
            <Radio id="normal" value="normal" />
            <Label htmlFor="normal">Normal</Label>
            <Description>
              Gaussian distribution; best for real-valued outcomes.
            </Description>
          </RadioField>
        </RadioGroup>
        {errors.prior_type ? (
          <p className="text-red-500 text-xs mt-1">{errors.prior_type}</p>
        ) : (
          <p className="text-red-500 text-xs mt-1">&nbsp;</p>
        )}

        <DividerWithTitle title="Outcome Type" />
        <RadioGroup
          name="rewardType"
          defaultValue=""
          onChange={(value) => updateRewardType(value as RewardType)}
          value={experimentState.reward_type}
        >
          <div className="mb-4" />
          <Label>Select an outcome type for the experiment</Label>
          <RadioField>
            <Radio id="real-valued" value="real-valued" />
            <Label htmlFor="real-valued">Real-valued</Label>
            <Description>
              E.g. how long someone engaged with your app, how long did
              onboarding take, etc.
            </Description>
          </RadioField>

          <RadioField>
            <Radio id="binary" value="binary" />
            <Label htmlFor="binary">Binary</Label>
            <Description>
              E.g. whether a user clicked on a button, whether a user converted,
              etc.
            </Description>
          </RadioField>
        </RadioGroup>
        {errors.reward_type ? (
          <p className="text-red-500 text-xs mt-1">{errors.reward_type}</p>
        ) : (
          <p className="text-red-500 text-xs mt-1">&nbsp;</p>
        )}
      </Fieldset>
    </div>
  );
}
