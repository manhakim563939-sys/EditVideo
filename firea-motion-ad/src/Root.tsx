import {Composition} from 'remotion';
import {FireaAd} from './FireaAd';
import T from './timeline.json';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="FireaAd"
    component={FireaAd}
    durationInFrames={T.durationInFrames}
    fps={T.fps}
    width={1080}
    height={1920}
  />
);
