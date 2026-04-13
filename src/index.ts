import React, { Fragment } from "react";
import { registerRoot, Composition } from "remotion";
import { ReelComposition } from "./Video";

const RemotionRoot: React.FC = () => {
    let inputProps;
    try {
        inputProps = require("../assets/temp/reel_data.json");
    } catch (e) {
        console.warn("Could not load reel_data.json, using defaults");
        inputProps = {
            duration: 10,
            fps: 30,
            width: 1080,
            height: 1920
        };
    }

    const durationInFrames = Math.ceil(inputProps.duration * inputProps.fps);

    return React.createElement(Fragment, null,
        React.createElement(Composition, {
            id: "ReelComposition",
            component: ReelComposition,
            durationInFrames: durationInFrames,
            fps: inputProps.fps,
            width: inputProps.width,
            height: inputProps.height
        })
    );
};

registerRoot(RemotionRoot);
