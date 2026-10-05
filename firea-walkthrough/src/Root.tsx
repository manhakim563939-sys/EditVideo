import {Composition} from 'remotion';
import {FireaWalkthrough} from './FireaWalkthrough';
import T from './timeline.json';

export const RemotionRoot: React.FC = () => (
  <Composition id="FireaWalkthrough" component={FireaWalkthrough} durationInFrames={T.durationInFrames} fps={T.fps} width={1080} height={1920} />
);
