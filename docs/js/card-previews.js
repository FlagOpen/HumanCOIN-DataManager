export function mediaUrl(ref, extension) {
  return new RegExp(`^media/[a-f0-9]{64}\\.${extension}$`).test(ref?.path || '')
    ? new URL(`../data/${ref.path}`, import.meta.url).href : null;
}
