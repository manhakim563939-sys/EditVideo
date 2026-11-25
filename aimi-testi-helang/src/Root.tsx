import { Composition } from "remotion";
import { Main } from "./Main";
import tl from "./timeline.json";

export const RemotionRoot = () => (
  <Composition id="Main" component={Main} durationInFrames={Math.ceil((tl.dialogEnd + tl.endCard) * tl.fps)} fps={tl.fps} width={1080} height={1920} />
);
