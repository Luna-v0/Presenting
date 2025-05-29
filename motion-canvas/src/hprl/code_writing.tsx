import {makeScene2D, Txt} from '@motion-canvas/2d';
import {createRef, waitFor, loop, all, cancel} from '@motion-canvas/core';

export default makeScene2D(function* (view) {
  const typing = createRef<Txt>();
  const cursor = createRef<Txt>();



  // Add text area
  view.add(
    <Txt
      ref={typing}
      fontFamily="JetBrains Mono"
      fontSize={40}
      fill="white"
      text=""
      x={-400}
      y={0}
      width={800}
      textWrap={true}
      lineHeight={1.4}
    />
  );

  // Add cursor
  view.add(
    <Txt
      ref={cursor}
      text="|"
      fontFamily="JetBrains Mono"
      fontSize={40}
      fill="white"
      x={-400}
      y={0}
    />
  );

  // Typing function
  function* typeText(text: string) {
    let current = '';
    for (let i = 0; i < text.length; i++) {
      const char = text[i];
      current += char;
      yield* typing().text(current, 0.01);
      cursor().position.x(typing().width() - 390); // Adjust for x offset
      yield* waitFor(char === ' ' ? 0.2 : 0.08);
    }
  }

  // Blink loop for cursor
  const blinking = loop(Infinity, function* () {
    yield* cursor().opacity(0, 0.5);
    yield* cursor().opacity(1, 0.5);
  });

  // Start typing
  yield* waitFor(0.5);
  yield* typeText(`def R(s, a, s_next):\n    return s + a + s_next`);

  // Stop blinking if needed
  cancel(blinking);
});