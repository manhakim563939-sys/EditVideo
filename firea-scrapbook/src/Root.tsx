import {Composition} from 'remotion';
import {FireaScrapbook} from './FireaScrapbook';
import T from './timeline.json';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="FireaScrapbook"
    component={FireaScrapbook}
    durationInFrames={T.durationInFrames}
    fps={T.fps}
    width={1080}
    height={1920}
  />
);
