import { Step } from "../../types";
import AddMABArms from "./mabs/addMABArms";
import MABPriorRewardSelection from "./mabs/addPriorReward";
import AddCMABArms from "./cmabs/addCMABArms";
import AddCMABContexts from "./cmabs/addCMABContext";
import CMABPriorRewardSelection from "./cmabs/addPriorReward";
import AddABArms from "./bayes_ab/addABArms";
import AddNotifications from "./addNotifications";

// --- MAB types and steps ---

const MABsteps: Step[] = [
  {
    name: "Configure MAB",
    component: MABPriorRewardSelection,
  },
  {
    name: "Add Arms",
    component: AddMABArms,
  },
  { name: "Notifications", component: AddNotifications },
];

// --- CMAB test types and steps ---

const CMABsteps: Step[] = [
  {
    name: "Configure MAB",
    component: CMABPriorRewardSelection,
  },
  {
    name: "Add Contexts",
    component: AddCMABContexts,
  },
  {
    name: "Add Arms",
    component: AddCMABArms,
  },
  { name: "Notifications", component: AddNotifications },
];

// --- A/B test types and steps ---

const ABsteps: Step[] = [
  {
    name: "Add Arms",
    component: AddABArms,
  },
  { name: "Notifications", component: AddNotifications },
];

// --- All steps ---

const AllSteps = {
  mab: MABsteps,
  cmab: CMABsteps,
  ab: ABsteps,
};

export { AllSteps };
