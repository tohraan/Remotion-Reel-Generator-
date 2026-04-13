import React, { useMemo } from "react";
import {
    AbsoluteFill,
    Audio,
    Sequence,
    useCurrentFrame,
    useVideoConfig,
    interpolate,
    Easing,
    Img,
    staticFile,
    random
} from "remotion";

// --- Config ---

const SAFE_TOP = 280;
const SAFE_BOTTOM = 220;

const PALETTE = {
    black_bg: "#050505",
    white_text: "#FFFFFF",
    gray_text: "#888888",
    neon_chartreuse: "#DFFF00",
    neon_glow: "rgba(223, 255, 0, 0.15)",
};

const TYPOGRAPHY = {
    primary: '"Helvetica Neue", "Helvetica", "Arial", sans-serif',
    weights: {
        light: 300,
        medium: 500,
        bold: 700,
        black: 900
    },
};

// --- Types ---

interface WordTiming {
    word: string;
    start: number;
    end: number;
}

interface ReelProps {
    script: string;
    voiceover_path: string;
    word_timings: WordTiming[];
    cta_keyword?: string;
}

// --- Components ---

const SquareGrid: React.FC = () => {
    const GRID_SIZE = 80;
    const STROKE_WIDTH = 1.0;
    const OPACITY = 0.08;
    const width = 1080;
    const height = 1920;
    return (
        <svg width="100%" height="100%" style={{ position: 'absolute', pointerEvents: 'none', zIndex: 1 }}>
            {Array.from({ length: 15 }).map((_, i) => (<line key={`v-${i}`} x1={i * GRID_SIZE} y1="0" x2={i * GRID_SIZE} y2={height} stroke={`rgba(255,255,255,${OPACITY})`} strokeWidth={STROKE_WIDTH} />))}
            {Array.from({ length: 25 }).map((_, i) => (<line key={`h-${i}`} x1="0" y1={i * GRID_SIZE} x2={width} y2={i * GRID_SIZE} stroke={`rgba(255,255,255,${OPACITY})`} strokeWidth={STROKE_WIDTH} />))}
        </svg>
    );
};

const SolidFilledShape: React.FC<{ width: number; height: number; borderRadius?: number | string; position: React.CSSProperties; alphas: [number, number]; loopDuration: number; gradientType: 'circle' | 'ellipse'; blur: number; motion: { x: number; y: number; rotate: number; } }> = ({ width, height, borderRadius = '50%', position, alphas, loopDuration, gradientType, blur, motion }) => {
    const frame = useCurrentFrame();
    const currentAlpha = interpolate(frame % loopDuration, [0, loopDuration / 2, loopDuration], [alphas[0], alphas[1], alphas[0]], { easing: Easing.inOut(Easing.sin) });
    const centerColor = `rgba(223, 255, 0, ${currentAlpha.toFixed(3)})`;
    const midColor = `rgba(223, 255, 0, ${(currentAlpha * 0.3).toFixed(3)})`;
    const edgeColor = `rgba(223, 255, 0, 0)`;
    const gradient = gradientType === 'circle' ? `radial-gradient(circle at center, ${centerColor} 0%, ${midColor} 50%, ${edgeColor} 100%)` : `radial-gradient(ellipse 120% 100% at 30% 50%, ${centerColor} 0%, ${midColor} 60%, ${edgeColor} 100%)`;
    return (<div style={{ position: 'absolute', width, height, borderRadius: borderRadius as any, ...position, background: gradient, transform: `translate(${interpolate(frame, [0, 900], [0, motion.x])}px, ${interpolate(frame, [0, 900], [0, motion.y])}px) rotate(${interpolate(frame, [0, 900], [0, motion.rotate])}deg)`, filter: `blur(${blur}px)`, pointerEvents: 'none', zIndex: 1, mixBlendMode: 'screen' }} />);
};

const AbstractElements: React.FC = () => (
    <AbsoluteFill style={{ zIndex: 1, pointerEvents: 'none', overflow: 'hidden' }}>
        <SolidFilledShape width={700} height={700} position={{ top: -350, left: -350 }} alphas={[0.15, 0.25]} loopDuration={120} gradientType="circle" blur={10} motion={{ x: 30, y: 0, rotate: 0 }} />
        <SolidFilledShape width={500} height={650} borderRadius="12px" position={{ top: 215, right: -250 }} alphas={[0.10, 0.20]} loopDuration={150} gradientType="ellipse" blur={15} motion={{ x: 0, y: -35, rotate: 6 }} />
        <SolidFilledShape width={900} height={900} position={{ bottom: -450, left: 200 }} alphas={[0.12, 0.22]} loopDuration={180} gradientType="circle" blur={20} motion={{ x: -60, y: 0, rotate: 0 }} />
        <SolidFilledShape width={600} height={600} position={{ bottom: -200, right: -200 }} alphas={[0.10, 0.18]} loopDuration={160} gradientType="circle" blur={12} motion={{ x: -20, y: -20, rotate: 0 }} />
    </AbsoluteFill>
);

const BackgroundLayer: React.FC = () => (
    <AbsoluteFill style={{ backgroundColor: PALETTE.black_bg, zIndex: 0 }}>
        <AbsoluteFill style={{ background: `radial-gradient(circle at center, #111111 0%, ${PALETTE.black_bg} 70%)` }} />
        <AbstractElements />
        <SquareGrid />
    </AbsoluteFill>
);

const BlockHighlighter: React.FC<{ progress: number; width: number }> = ({ progress, width }) => {
    return (
        <div style={{
            position: 'absolute',
            top: '-5%',
            left: 0,
            width: width,
            height: '110%',
            backgroundColor: PALETTE.neon_chartreuse,
            transform: `scaleX(${progress})`,
            transformOrigin: 'left',
            zIndex: -1,
        }} />
    );
};

// Header Logo (Visible during Body, Hides during CTA)
const LogoHeader: React.FC<{ show: boolean }> = ({ show }) => {
    let logoSrc;
    try { logoSrc = require("../assets/brand_logo.jpg"); } catch (e) { logoSrc = ""; }
    if (!logoSrc) return null;
    return (
        <AbsoluteFill style={{ alignItems: 'center', zIndex: 20, pointerEvents: 'none', opacity: show ? 1 : 0, transition: 'opacity 0.2s ease-in-out' }}>
            <div style={{ position: 'absolute', top: 65, width: 160, height: 160 }}>
                <Img src={logoSrc} style={{ width: '100%', height: '100%', objectFit: 'contain', filter: 'invert(1)', mixBlendMode: 'screen' }} />
            </div>
        </AbsoluteFill>
    );
};

const FooterBranding: React.FC = () => (
    <AbsoluteFill style={{ pointerEvents: 'none', zIndex: 20, alignItems: 'center', justifyContent: 'flex-end', paddingBottom: 60 }}>
        <h2 style={{ fontSize: 24, fontWeight: TYPOGRAPHY.weights.black, letterSpacing: '0.4em', color: PALETTE.white_text, opacity: 0.3 }}>TRIAXON</h2>
    </AbsoluteFill>
);

// --- STACKED CTA ---
// Layout: Name -> Logo -> DM Text -> Follow Button
const CleanCTASequence: React.FC<{ startFrame: number; cta_keyword?: string }> = ({ startFrame, cta_keyword }) => {
    const frame = useCurrentFrame();
    if (frame < startFrame) return null;

    const localFrame = frame - startFrame;
    const contentOpacity = interpolate(localFrame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
    const contentScale = interpolate(localFrame, [0, 20], [0.95, 1.0], { extrapolateRight: 'clamp', easing: Easing.out(Easing.back(1.5)) });

    let logoSrc;
    try { logoSrc = require("../assets/brand_logo.jpg"); } catch (e) { logoSrc = ""; }

    const STACK_WIDTH = 500; // Consistent width for block

    return (
        <AbsoluteFill style={{ zIndex: 60, alignItems: 'center', justifyContent: 'center' }}>

            <div style={{
                width: '100%', height: '100%',
                display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 60,
                opacity: contentOpacity,
                transform: `scale(${contentScale})`
            }}>

                {/* 1. TRIAXON Name (Top) */}
                <h1 style={{
                    fontSize: 100, fontWeight: TYPOGRAPHY.weights.black, color: PALETTE.white_text,
                    letterSpacing: '-0.02em', margin: 0
                }}>
                    TRIAXON
                </h1>

                {/* 2. Logo (Middle) */}
                {logoSrc && (
                    <div style={{ width: 400, height: 400, margin: '-20px 0' }}>
                        <Img src={logoSrc} style={{ width: '100%', height: '100%', objectFit: 'contain', filter: 'invert(1)', mixBlendMode: 'screen' }} />
                    </div>
                )}

                {/* 3. DM TEXT */}
                <div style={{ width: STACK_WIDTH, textAlign: 'center' }}>
                    <h2 style={{ fontSize: 60, fontWeight: TYPOGRAPHY.weights.bold, color: PALETTE.neon_chartreuse, margin: 0, fontFamily: TYPOGRAPHY.primary }}>
                        DM '{cta_keyword || "EMAIL"}'
                    </h2>
                </div>

                {/* 4. Follow Button (Solid Green Block) */}
                <div style={{
                    width: STACK_WIDTH,
                    padding: '20px 0',
                    backgroundColor: PALETTE.neon_chartreuse,
                    borderRadius: 100, // Pill shape
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    marginTop: 0,
                    boxShadow: `0 10px 30px ${PALETTE.neon_glow}`
                }}>
                    <span style={{
                        fontSize: 32, fontWeight: TYPOGRAPHY.weights.black, letterSpacing: '0.1em',
                        color: PALETTE.black_bg, // Black Text on Green
                        textTransform: 'uppercase'
                    }}>
                        FOLLOW
                    </span>
                </div>

            </div>
        </AbsoluteFill>
    );
};

// --- Typography ---

const TypewriterWord: React.FC<{ word: string; startFrame: number; endFrame: number; frame: number; isBold: boolean; isHighlighter: boolean; }> = ({ word, startFrame, endFrame, frame, isBold, isHighlighter }) => {

    const progress = interpolate(frame, [startFrame, endFrame], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
    const charWidth = isBold ? 40 : 32;
    const wordWidth = word.length * charWidth;

    // Text Color Logic: White normally, Black if Highlighted
    const textColor = isHighlighter && progress > 0.1 ? PALETTE.black_bg : PALETTE.white_text;

    return (
        <span style={{
            display: "inline-block", whiteSpace: "nowrap", marginRight: "0.20em",
            fontWeight: isBold ? TYPOGRAPHY.weights.bold : TYPOGRAPHY.weights.light,
            color: textColor, position: 'relative', zIndex: 1
        }}>
            {isHighlighter && (<BlockHighlighter progress={progress} width={wordWidth} />)}
            {word.split("").map((char, i) => {
                const step = 1 / (word.length + 2);
                const charProg = interpolate(progress, [i * step, i * step + (step * 3)], [0, 1], { extrapolateRight: 'clamp' });
                const y = interpolate(charProg, [0, 1], [10, 0], { easing: Easing.out(Easing.quad) });
                return (<span key={i} style={{ display: 'inline-block', opacity: charProg, transform: `translateY(${y}px)` }}>{char}</span>);
            })}
        </span>
    );
};

const SentenceBlock: React.FC<{ words: WordTiming[]; fps: number; frame: number; isHook: boolean; layoutTop: number; opacity: number; blur: number; }> = ({ words, fps, frame, isHook, layoutTop, opacity, blur }) => {
    const sorted = [...words].sort((a, b) => b.word.length - a.word.length);
    const candidate = sorted[0];
    const emphasisWord = (candidate && candidate.word.length > 5) ? candidate.word : null;

    let hookScale = 1;
    if (isHook) { hookScale = interpolate(frame, [0, 20], [3.0, 1.0], { extrapolateRight: 'clamp', easing: Easing.out(Easing.exp) }); }

    const style = isHook ?
        { fontSize: 130, lineHeight: 1.0, letterSpacing: '-0.05em', fontWeight: TYPOGRAPHY.weights.bold, transform: `scale(${hookScale})`, transformOrigin: 'center center' } :
        { fontSize: 85, lineHeight: 1.15, letterSpacing: '-0.03em', fontWeight: TYPOGRAPHY.weights.medium };

    return (
        <div style={{ position: 'absolute', top: isHook ? layoutTop - 100 : layoutTop, left: 0, width: '100%', textAlign: isHook ? 'center' : 'left', ...style, opacity, filter: `blur(${blur}px)`, zIndex: 5 }}>
            {words.map((w, i) => (
                <TypewriterWord key={i} word={w.word} startFrame={w.start * fps} endFrame={w.end * fps} frame={frame} isBold={isHook || w.word === emphasisWord} isHighlighter={!isHook && w.word === emphasisWord} />
            ))}
        </div>
    );
};

// --- Main Composition ---

export const ReelComposition: React.FC = () => {
    let inputProps: ReelProps;
    try { inputProps = require("../assets/temp/reel_data.json"); } catch (e) { inputProps = {} as ReelProps; }

    const { fps, width, height } = useVideoConfig();
    const frame = useCurrentFrame();

    const marginX = width * 0.15;
    const contentWidth = width - (marginX * 2);
    const layoutAnchor = SAFE_TOP + (height - SAFE_TOP - SAFE_BOTTOM) * 0.4;

    // PARSE Logic: Separate CTA (Last Sentence) from Body
    const { bodyGroups, ctaStartFrame } = useMemo(() => {
        if (!inputProps.word_timings) return { bodyGroups: [], ctaStartFrame: 0 };

        const rawGroups: WordTiming[][] = [];
        let temp: WordTiming[] = [];
        inputProps.word_timings.forEach((t) => {
            temp.push(t);
            if (/[.!?]$/.test(t.word)) { rawGroups.push(temp); temp = []; }
        });
        if (temp.length > 0) rawGroups.push(temp);

        // Last Group is CTA
        const ctaGroup = rawGroups.pop();
        const ctaStart = ctaGroup ? ctaGroup[0].start * fps : 10000;

        // Process Body Groups
        const processedBody = rawGroups.map((words, idx) => {
            const startFr = words[0].start * fps;
            const endFr = words[words.length - 1].end * fps;
            let fadeStart = endFr + 60; // Dwell
            let fadeEnd = fadeStart + 20; // Exit
            if (rawGroups[idx + 1]) {
                const nextStart = rawGroups[idx + 1][0].start * fps;
                if (fadeEnd > nextStart) { fadeEnd = Math.max(endFr + 20, nextStart - 5); fadeStart = fadeEnd - 20; }
            }
            if (fadeEnd > ctaStart) { fadeEnd = ctaStart; fadeStart = fadeEnd - 10; }
            return { words, startFr, endFr, fadeStart, fadeEnd };
        });

        return { bodyGroups: processedBody, ctaStartFrame: ctaStart };
    }, [inputProps.word_timings, fps]);

    const topLogoVisible = frame < ctaStartFrame;

    return (
        <AbsoluteFill style={{ backgroundColor: PALETTE.black_bg, fontFamily: TYPOGRAPHY.primary, color: PALETTE.white_text }}>
            <BackgroundLayer />

            <LogoHeader show={topLogoVisible} />

            {/* Main Text (Body Only) */}
            <div style={{ position: 'absolute', top: 0, left: marginX, width: contentWidth, height: height, zIndex: 5 }}>
                {bodyGroups.map((sent, idx) => {
                    const { startFr, fadeStart, fadeEnd } = sent;
                    let opacity = 1; let blur = 0;
                    if (frame < startFr || frame > fadeEnd) opacity = 0;
                    else if (frame > fadeStart) {
                        const p = interpolate(frame, [fadeStart, fadeEnd], [0, 1], { extrapolateRight: 'clamp' });
                        opacity = 1 - p; blur = p * 10;
                    }
                    if (opacity === 0) return null;
                    return <SentenceBlock key={idx} words={sent.words} fps={fps} frame={frame} isHook={idx === 0} layoutTop={layoutAnchor} opacity={opacity} blur={blur} />;
                })}
            </div>

            {/* Stacked CTA (Starts exactly when CTA Audio starts) */}
            <CleanCTASequence startFrame={ctaStartFrame} cta_keyword={inputProps.cta_keyword} />

            <FooterBranding />
            {inputProps.voiceover_path && <Audio src={inputProps.voiceover_path} />}
        </AbsoluteFill>
    );
};
