import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

const font = 'DejaVu Sans, Liberation Sans, Arial, sans-serif';

export const RenderTest: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();

  const titleIn = spring({frame, fps, config: {damping: 12}});
  const subOpacity = interpolate(frame, [20, 40], [0, 1], {extrapolateRight: 'clamp'});
  const circleX = interpolate(frame, [0, durationInFrames - 1], [-200, 2120]);
  const squareRot = interpolate(frame, [0, durationInFrames - 1], [0, 360]);
  const barW = interpolate(frame, [0, durationInFrames - 1], [0, 1920]);
  const seconds = (frame / fps).toFixed(1);

  return (
    <AbsoluteFill style={{backgroundColor: '#14213d', fontFamily: font}}>
      <div style={{position: 'absolute', left: circleX, top: 120, width: 200, height: 200, borderRadius: '50%', background: '#fca311'}} />
      <div style={{position: 'absolute', right: 180, bottom: 200, width: 220, height: 220, background: '#e63946', transform: `rotate(${squareRot}deg)`}} />
      <div style={{position: 'absolute', left: 160, bottom: 220, width: 0, height: 0, borderLeft: '120px solid transparent', borderRight: '120px solid transparent', borderBottom: '200px solid #2a9d8f'}} />
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
        <div style={{color: 'white', fontSize: 140, fontWeight: 800, transform: `scale(${titleIn})`}}>Render Test</div>
        <div style={{color: '#e5e5e5', fontSize: 56, opacity: subOpacity, marginTop: 20}}>Remotion + Node.js + ffmpeg</div>
        <div style={{color: '#fca311', fontSize: 64, marginTop: 40, fontVariantNumeric: 'tabular-nums'}}>{seconds}s</div>
      </AbsoluteFill>
      <div style={{position: 'absolute', left: 0, bottom: 0, height: 24, width: barW, background: '#fca311'}} />
    </AbsoluteFill>
  );
};
