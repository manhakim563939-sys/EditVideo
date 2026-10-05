import {Composition} from 'remotion';
import {FireaLiquid} from './FireaLiquid';
import T from './timeline.json';

export const RemotionRoot: React.FC = () => (
  <Composition id="FireaLiquid" component={FireaLiquid} durationInFrames={T.durationInFrames} fps={T.fps} width={1080} height={1920} />
);
