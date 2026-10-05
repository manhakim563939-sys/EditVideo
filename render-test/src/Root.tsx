import React from 'react';
import {Composition} from 'remotion';
import {RenderTest} from './RenderTest';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="RenderTest"
    component={RenderTest}
    durationInFrames={150}
    fps={30}
    width={1920}
    height={1080}
  />
);
