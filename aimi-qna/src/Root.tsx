import { Composition } from "remotion";
import { QData, QnA } from "./QnA";
import q1 from "./data/q1.json";
import q2 from "./data/q2.json";
import q3 from "./data/q3.json";
import q4 from "./data/q4.json";
import q5 from "./data/q5.json";

const ALL = [q1, q2, q3, q4, q5] as unknown as QData[];

export const RemotionRoot = () => (
  <>
    {ALL.map((d) => (
      <Composition key={d.id} id={`QnA${d.no}`} component={QnA} defaultProps={{ d }} durationInFrames={Math.ceil(d.total * d.fps)} fps={d.fps} width={1080} height={1920} />
    ))}
  </>
);
