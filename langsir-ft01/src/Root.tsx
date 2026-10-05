import { Composition } from "remotion";
import { Main } from "./Main";
import tl from "./timeline.json";

export const RemotionRoot = () => {
  const dur = Math.ceil((tl.footageEnd + tl.endCardDur) * tl.fps);
  return (
    <Composition id="Main" component={Main} durationInFrames={dur} fps={tl.fps} width={1080} height={1920} />
  );
};
