import api from "@/utils/api";
import {
  MABExperimentStateNormal,
  MABExperimentStateBeta,
  ABExperimentState,
  CMABExperimentState,
} from "./types";
import { ExperimentState } from "./types";

const createNewExperiment = async ({
  experimentData,
  token,
}: {
  experimentData: ExperimentState;
  token: string | null;
}) => {
  let endpoint: string;
  let newExperimentData:
    | MABExperimentStateNormal
    | MABExperimentStateBeta
    | ABExperimentState
    | CMABExperimentState;

  if (experimentData.methodType == "mab") {
    endpoint = "/mab/";
    if (experimentData.priorType == "beta") {
      newExperimentData = experimentData as MABExperimentStateBeta;
    } else {
      newExperimentData = experimentData as MABExperimentStateNormal;
    }
  } else if (experimentData.methodType == "ab") {
    newExperimentData = experimentData as ABExperimentState;
    endpoint = "/ab/";
  } else if (experimentData.methodType == "cmab") {
    newExperimentData = experimentData as CMABExperimentState;
    endpoint = "/contextual_mab/";
  } else {
    throw new Error("Invalid experiment type");
  }

  const convertedData = {
    name: newExperimentData.name,
    description: newExperimentData.description,
    reward_type: newExperimentData.rewardType,
    prior_type: newExperimentData.priorType,
    arms: newExperimentData.arms,
    notifications: newExperimentData.notifications,
  };

  try {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    console.log(convertedData);
    const response = await api.post(endpoint, convertedData, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error: unknown) {
    if (error instanceof Error) {
      throw new Error(`Error creating new experiment: ${error.message}`);
    } else {
      throw new Error("Error creating new experiment");
    }
  }
};

const getAllMABExperiments = async (token: string | null) => {
  try {
    const response = await api.get("/mab/", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error: unknown) {
    if (error instanceof Error) {
      throw new Error(`Error fetching all experiments: ${error.message}`);
    } else {
      throw new Error("Error fetching all experiments");
    }
  }
};

const getAllCMABExperiments = async (token: string | null) => {
  try {
    const response = await api.get("/contextual_mab/", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error: unknown) {
    if (error instanceof Error) {
      throw new Error(`Error fetching all experiments: ${error.message}`);
    } else {
      throw new Error("Error fetching all experiments");
    }
  }
};

export { createNewExperiment, getAllMABExperiments, getAllCMABExperiments };
