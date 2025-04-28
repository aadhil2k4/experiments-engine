import { useState } from "react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { MABExperimentDetails } from "../types";
import { BetaLineChart, NormalLineChart } from "./Charts";

export default function MABChart({
  experimentData,
}: {
  experimentData: MABExperimentDetails | null;
}) {
  const [showPriors, setShowPriors] = useState(false);

  if (!experimentData) {
    return <div>No data available</div>;
  }

  const priorBetaData = experimentData.arms.map((arm) => ({
    name: arm.name,
    alpha: arm.alpha_init,
    beta: arm.beta_init,
  }));


  const posteriorBetaData = experimentData.arms.map((arm) => ({
    name: arm.name,
    alpha: arm.alpha,
    beta: arm.beta,
  }));

  const priorGaussianData = experimentData.arms.map((arm) => ({
    name: arm.name,
    mu: arm.mu_init,
    sigma: arm.sigma_init,
  }));

  const posteriorGaussianData = experimentData.arms.map((arm) => ({
    name: arm.name,
    mu: arm.mu,
    sigma: arm.sigma,
  }));

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex justify-between items-center">
          <div>
            <CardTitle className="text-lg">Experiment Results</CardTitle>
            <CardDescription>Plotting performance of each arm</CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <label htmlFor="show-priors" className="text-sm font-medium">
              Show Priors
            </label>
            <Switch
              id="show-priors"
              checked={showPriors}
              onCheckedChange={setShowPriors}
            />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[300px] w-full">
          {experimentData.prior_type == "beta" ? (
            <BetaLineChart posteriors={posteriorBetaData} priors={priorBetaData} showPriors={showPriors} />
          ) : (
            <NormalLineChart posteriors={posteriorGaussianData} priors={priorGaussianData} showPriors={showPriors} />
          )}
        </div>
      </CardContent>
    </Card>
  );
}
