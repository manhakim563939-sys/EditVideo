import {Composition} from 'remotion';
import {FireaRetro} from './FireaRetro';
import T from './timeline.json';

export const RemotionRoot: React.FC = () => (
  <Composition id="FireaRetro" component={FireaRetro} durationInFrames={T.durationInFrames} fps={T.fps} width={1080} height={1920} />
);
