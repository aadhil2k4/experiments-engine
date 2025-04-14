import {
  Card,
  CardContent,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { MABBeta, MABNormal, CMAB, BayesianAB, MethodType } from "../types";
import { MABBetaCards, MABNormalCards } from "./cards/createMABCard";
import { CMABCards } from "./cards/createCMABCard";
import { BayesianABCards } from "./cards/createBayesABCard";

export default function ExperimentCards({
  experiment,
  methodType,
}: {
  experiment: MABBeta | MABNormal | CMAB | BayesianAB;
  methodType: MethodType;
}) {
  if (methodType === "mab" && experiment.prior_type === "beta") {
    const betaExperiment = experiment as MABBeta;
    return <MABBetaCards experiment={betaExperiment} />;
  } else if (methodType === "mab" && experiment.prior_type === "normal") {
    const normalExperiment = experiment as MABNormal;
    return <MABNormalCards experiment={normalExperiment} />;
  } else if (methodType === "cmab") {
    const cmabExperiment = experiment as CMAB;
    return <CMABCards experiment={cmabExperiment} />;
  } else if (methodType === "bayes_ab") {
    const bayesExperiment = experiment as BayesianAB;
    return <BayesianABCards experiment={bayesExperiment} />;
  }

  // Default case for other experiment types
  return (
    <Card>
      <CardContent>
        <CardTitle>Unsupported Experiment Type</CardTitle>
        <CardDescription>
          This experiment type is not yet supported.
        </CardDescription>
      </CardContent>
    </Card>
  );
}
