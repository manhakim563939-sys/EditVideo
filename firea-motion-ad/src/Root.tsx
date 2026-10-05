import React from "react";
import { Composition } from "remotion";
import { FireaAd } from "./FireaAd";
import TL from "./timeline.json";

export const Root: React.FC = () => (
  <Composition
    id="FireaAd"
    component={FireaAd}
    width={1080}
    height={1920}
    fps={TL.fps}
    durationInFrames={TL.durationInFrames}
  />
);
