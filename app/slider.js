import { useState } from "react";

export default function Slider({ minValue, maxValue, defaultValue, step }) {
    const [value, setValue] = useState(defaultValue);

    console.log(minValue);

    return (
        <>
            <input type="range"
                min={minValue}
                max={maxValue}
                defaultValue={defaultValue}
                step={step}
                onInput={(e) => setValue(e.target.value)} />
            <span>{value}</span>
        </>
    )
};
