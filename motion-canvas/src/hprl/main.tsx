import rewardFunction from "./reward_function";
import rewardCode from "./reward_code";
import { Latex, Layout, makeScene2D } from "@motion-canvas/2d";
import { createRef, waitFor } from "@motion-canvas/core";

export default makeScene2D(function* (view) {
  // yield* rewardFunction(view);
  yield* rewardCode(view);
});
