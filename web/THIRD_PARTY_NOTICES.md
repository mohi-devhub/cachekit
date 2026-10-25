# UI sources and licenses

Exact npm versions and integrity hashes are committed in package-lock.json.
Runtime assets are bundled locally; these are source references, not CDN requests.

| Dependency | Version | Use / terms |
| --- | --- | --- |
| [GSAP](https://gsap.com/docs/v3/) | 3.15.0 | Prefix transition, summary fade and measured-value interpolation. [Standard license](https://gsap.com/standard-license/). |
| [Lenis](https://github.com/darkroomengineering/lenis) | 1.3.27 | Optional desktop overview scrolling; MIT, [license copy](public/licenses/Lenis-LICENSE.txt). |
| [Inter](https://fontsource.org/fonts/inter) | Fontsource Variable 5.3.0 | Local Latin variable UI font; [OFL copy](public/licenses/Inter-OFL.txt). |
| [Source Serif 4](https://fontsource.org/fonts/source-serif-4) | Fontsource Variable 5.3.1 | Local Latin variable explanatory font; [OFL copy](public/licenses/Source-Serif-4-OFL.txt). |
| [Geist Mono](https://fontsource.org/fonts/geist-mono) | Fontsource Variable 5.3.0 | Local Latin variable code font; [OFL copy](public/licenses/Geist-Mono-OFL.txt). |

One React Bits component is adapted in
[src/components/react-bits/fade-content.tsx](src/components/react-bits/fade-content.tsx)
from [FadeContent at e12c22192ac7b4b452c5e2feb9b586d74765d696](https://github.com/DavidHDev/react-bits/blob/e12c22192ac7b4b452c5e2feb9b586d74765d696/src/ts-default/Animations/FadeContent/FadeContent.tsx),
following the [copy-source workflow](https://reactbits.dev/animations/fade-content).
Copyright (c) 2026 David Haz. Its [MIT + Commons Clause license](public/licenses/React-Bits-LICENSE.md)
remains applicable to that adaptation; it is not relicensed under this project's
license. The adaptation retains only the mount/fade path, removes filters,
ScrollTrigger and repeating effects, and responds to reduced motion. It is used
within this application, not distributed as a component pack.

The theme follows the participant's supplied palette and typography direction.
No Cognition/Devin logos, proprietary fonts or copied marketing text are used.

The original cache-scanner illustration uses the vendored [Anatomy geometry kit](https://github.com/wheresryan22/anatomy), copyright2026 Ryan, under its [MIT license](src/components/iso/LICENSE). Exact vendored bytes are identified in [the source record](../eval_results/setup/anatomy_source.json). No model/network/runtime dependency is added by this geometry.
