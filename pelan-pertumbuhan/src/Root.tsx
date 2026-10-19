import { Composition } from "remotion";
import { Main } from "./Main";
import tl from "./timeline.json";

export const RemotionRoot = () => (
  <Composition id="Main" component={Main} durationInFrames={Math.ceil(tl.total * tl.fps)} fps={tl.fps} width={1920} height={1080} />
);
