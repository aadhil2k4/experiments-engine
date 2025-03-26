"use client";
import React, { useEffect } from "react";
import EmptyPage from "./components/EmptyPage";
import { getAllMABExperiments, getAllCMABExperiments } from "./api";
import { MABBeta, MABNormal, CMAB, MethodType } from "./types";
import ExperimentCard from "./components/ExperimentCard";
import Hourglass from "@/components/Hourglass";
import FloatingAddButton from "./components/FloatingAddButton";
import { Link } from "@/components/catalyst/link";
import { useAuth } from "@/utils/auth";
import { DividerWithTitle } from "@/components/Dividers";

export default function Experiments() {
  const [haveExperiments, setHaveExperiments] = React.useState(false);
  const [mabExperiments, setMABExperiments] = React.useState<MABBeta[]>([]);
  const [cmabExperiments, setCMABExperiments] = React.useState<CMAB[]>([]);
  const [loading, setLoading] = React.useState(true);

  const { token } = useAuth();

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    getAllMABExperiments(token).then((data) => {
      setMABExperiments(data);
    });
    getAllCMABExperiments(token).then((data) => {
      setCMABExperiments(data);
    });
    setLoading(false);
  }, [token]);

  useEffect(() => {
    if (mabExperiments.length > 0 || cmabExperiments.length > 0) {
      setHaveExperiments(true);
    } else {
      setHaveExperiments(false);
    }
  }, [mabExperiments, cmabExperiments]);

  return loading ? (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white dark:bg-zinc-950 rounded-lg p-6 sm:p-8 md:p-10 flex flex-col items-center justify-center space-y-4 w-full max-w-sm mx-auto">
        <Hourglass />
        <span className="text-primary font-medium text-center">Loading...</span>
      </div>
    </div>
  ) : haveExperiments ? (
    <div className="flex flex-col space-y-8">
      {mabExperiments.length > 0 && (
        <div>
          <DividerWithTitle title="Multi-Armed Bandit Experiments" />
          <div className="my-4"></div>
          <div>
            <ExperimentCardGrid experiments={mabExperiments} methodType="mab" />
          </div>
        </div>
      )}
      {cmabExperiments.length > 0 && (
        <div>
          <DividerWithTitle title="Contextual Multi-Armed Bandit Experiments" />
          <div className="my-4"></div>
          <div>
            <ExperimentCardGrid
              experiments={cmabExperiments}
              methodType="cmab"
            />
            <Link href="/experiments/add">
              <FloatingAddButton />
            </Link>
          </div>
        </div>
      )}
      <Link href="/experiments/add">
        <FloatingAddButton />
      </Link>
    </div>
  ) : (
    <div
      className="grid grow grid-rows-1 items-center justify-items-center sm:p-20 "
      style={{ minHeight: "calc(100vh - 200px)" }}
    >
      <main className="flex flex-col gap-8 row-start-1 items-center sm:items-start">
        <span className="content-center grow">
          <EmptyPage />
        </span>
      </main>
    </div>
  );
}

const ExperimentCardGrid = ({
  experiments,
  methodType,
}: {
  experiments: MABBeta[] | MABNormal[] | CMAB[];
  methodType: MethodType;
}) => {
  return (
    <ul
      role="list"
      className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 items-stretch"
    >
      {experiments.map((experiment) => (
        <li key={experiment.experiment_id}>
          <ExperimentCard experiment={experiment} methodType={methodType} />
        </li>
      ))}
    </ul>
  );
};
