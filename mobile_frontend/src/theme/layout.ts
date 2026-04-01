export const DESIGN_WIDTH = 412;

export const getScale = (width: number) => {
  const raw = width / DESIGN_WIDTH;
  return Math.max(0.84, Math.min(raw, 1.08));
};

export const rs = (size: number, scale: number) => Math.round(size * scale);
