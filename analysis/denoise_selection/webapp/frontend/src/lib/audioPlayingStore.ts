/** Global audio playback flag — read by ScopeCanvas without React re-renders. */
export const audioPlayingStore = {
  playing: false,
};

export function setAudioPlaying(playing: boolean): void {
  audioPlayingStore.playing = playing;
}
