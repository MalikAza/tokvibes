"""
MIDI Song Database for TokVibes

This file contains the configuration for MIDI songs used by the game.
You can add your own MIDI files by placing them in the MIDI directory
and adding an entry to the ALL_SONG list below.

Song Dictionary Parameters:
---------------------------
name: Display name of the song
path: Path to the MIDI/MP3 file (relative to src directory)
volume: Volume multiplier (0.0 to 1.0)
skip_first_beats: Number of initial beats to skip (useful for intros)
"""

ALL_SONG = [
    {
        "name": "Im blue",
        "path": "Musics/MIDI/im_blue.mid",
        "volume": 0.1,
        "skip_first_beats": 34
    },
]