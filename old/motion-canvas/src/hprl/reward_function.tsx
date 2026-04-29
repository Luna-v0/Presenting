import { Latex, View2D } from "@motion-canvas/2d";
import { all, createRef, waitFor } from "@motion-canvas/core";

export default function* rewardFunction(view: View2D) {
  const tex = createRef<Latex>();

  const r_tex = ["\\textcolor{purple}{r_t}", "=R(s_t,a_t,s_{t+1})"];
  const q_text = [
    "Q(s_t,a_t) = \\sum_{s_{t+1}} P(s_{t+1}|s_t,a_t)\\left[",
    "\\textcolor{purple}{r_t}",
    "+ \\gamma \\max_{a_{t+1}} Q(s_{t+1},a_{t+1})\\right]",
  ];
  const v_text = [
    "V(s_t) = \\sum_{a_t} \\pi(a_t|s_t)\\left[",
    "\\textcolor{purple}{r_t}",
    " + \\gamma \\max_{a_{t+1}} Q(s_{t+1},a_{t+1})\\right]",
  ];

  view.fill("#fff");
  view.add(<Latex ref={tex} tex={r_tex} fill="black" fontSize={65} />);
  yield* waitFor(2);

  yield* all(
    yield* tex().tex(q_text, 2),
    yield* waitFor(1),
    yield* tex().tex(v_text, 2),
    yield* waitFor(1),
    yield* tex().tex(r_tex, 2),
    yield* tex().opacity(0, 0),
  );

  tex().remove();
}

