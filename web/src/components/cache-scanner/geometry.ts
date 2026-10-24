import * as k from "../iso/iso-kit";

// World units are schematic geometry, never measured hardware or token counts.
const plate = { x: -174, y: -62, w: 348, d: 124, r: 6 };
export const travel = { start: -142, length: 284 };
export const projection = k.fitProjection(k.boxCorners(plate, -18, 64), 800, 330, { pad: 34, azimuth: 66, elevation: 34 });
export type Part = { id: string; paths: k.SolidPaths; center: k.Point3; moving?: boolean; color?: string };
const parts: Part[] = [];
function slab(id: string, p: k.Plan, z: number, h: number, moving = false, color?: string) {
  parts.push({ id, paths: k.slabOf(p, z, h, projection, 5, 0.7), center: [p.x + p.w / 2, p.y + p.d / 2, z + h / 2], moving, color });
}
function round(id: string, x: number, y: number, r: number, z: number, h: number, moving = false, color?: string) {
  parts.push({ id, paths: k.cylinder(x, y, r, z, h, projection, 24, 0.35), center: [x, y, z + h / 2], moving, color });
}
for (const [i, [x, y]] of k.corners(plate, 20).entries()) {
  round(`foot-${i}`, x, y, 8, -18, 3, false, "#a5a5a0");
  round(`flange-${i}`, x, y, 6, -15, 5);
}
slab("bedplate", plate, -10, 10, false, "#d9d9d3");
for (const [i, [x, y]] of k.corners(plate, 11).entries()) round(`base-screw-${i}`, x, y, 2, 0, 0.8, false, "#8c8c87");
for (const y of [-43, 43]) {
  for (const x of [-156, 156]) {
    slab(`mount-${x}-${y}`, { x: x - 6, y: y - 7, w: 12, d: 14, r: 2 }, 0, 5);
    round(`mount-bolt-${x}-${y}`, x, y, 1.4, 5, 0.8, false, "#7c7c78");
  }
  slab(`rail-${y}`, { x: -156, y: y - 2, w: 312, d: 4, r: 1 }, 5, 4, false, "#b8b9b3");
  for (const x of [-162, 158]) slab(`end-stop-${x}-${y}`, { x, y: y - 6, w: 4, d: 12, r: 1 }, 5, 10);
}
slab("tape-tray", { x: -150, y: -20, w: 300, d: 40, r: 2 }, 0, 6, false, "#b5b6b0");
for (const y of [-21, 18]) slab(`retaining-lip-${y}`, { x: -150, y, w: 300, d: 3, r: 0.6 }, 6, 4);
slab("ruler", { x: -147, y: 26, w: 294, d: 7, r: 0.8 }, 0, 1, false, "#d0d0c8");
const ticks = k.topTicks(-142, 142, 7.1, 4, 26.5, 1.1, [2, 5], projection);
export const rulerTicks = ticks.minor + ticks.major;
export const groove = k.planOutline(k.insetPlan(plate, 4), 0.15, projection, 5);
for (const y of [-43, 43]) {
  slab(`bearing-${y}`, { x: -8, y: y - 7, w: 16, d: 14, r: 2 }, 9, 7, true, "#c0c1bb");
  slab(`column-${y}`, { x: -4, y: y - 4, w: 8, d: 8, r: 1 }, 16, 35, true);
  round(`bearing-screw-${y}`, 0, y, 1.7, 16, 0.8, true, "#686963");
}
slab("bridge", { x: -6, y: -48, w: 12, d: 96, r: 2 }, 51, 7, true, "#d4d5cf");
slab("sensor", { x: -10, y: -10, w: 20, d: 20, r: 2 }, 36, 15, true, "#363832");
slab("sensor-cap", { x: -8, y: -8, w: 16, d: 16, r: 1 }, 51, 9, true, "#484b43");
round("sensor-lamp", 0, 0, 2.5, 60, 1, true, "#2200ff");
round("probe-stem", 0, 0, 2, 17, 19, true, "#84877e");
round("lens-barrel", 0, 0, 4, 11, 6, true, "#383b33");
round("lens", 0, 0, 3, 9.5, 1.5, true, "#2200ff");
for (const y of [-43, 43]) round(`bridge-bolt-${y}`, 0, y, 1.7, 58, 0.8, true, "#75786e");
export const scannerParts = parts;
export const tapeParts = Array.from({ length: 18 }, (_, i) => {
  const w = travel.length / 18, x = travel.start + i * w;
  return { id: `tape-${i}`, paths: k.slabOf({ x: x + 0.5, y: -16, w: w - 1, d: 32, r: 0.3 }, 6, 3, projection, 2, 0.3), center: [x + w / 2, 0, 7.5] as k.Point3,
    mark: k.iso([x + w / 2, 0, 9.2], projection), slash: k.lineOnTop([x + w / 2 - 2, 4], [x + w / 2 + 2, -4], 9.2, projection) };
});
export const scannerTransform = (fraction: number) => k.translateAlong(projection, [travel.start + fraction * travel.length, 0, 0]);
export const partDepth = (part: Part, fraction: number) => {
  // Long support solids span several depths; their center alone would paint
  // over objects resting on them. Preserve mounting layers before depth sorting.
  const layer = part.moving ? 5 : part.id.startsWith("tape-") && part.id !== "tape-tray" ? 4
    : part.id.startsWith("foot-") || part.id.startsWith("flange-") ? 0 : part.id === "bedplate" ? 1 : 2;
  return layer * 1000 + k.depthOf([part.center[0] + (part.moving ? travel.start + fraction * travel.length : 0), part.center[1], part.center[2]], projection);
};
export const scanLine = k.lineOnTop([0, -18], [0, 18], 9.2, projection);
