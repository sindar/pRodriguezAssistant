## Your rude personal ASSistant:) [![ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/L3L32CDN6) <br> 
A Python version using pocketsphix.<br>
Work in progress(planned for release in 2096)...<br>

### 3D-model 
https://www.thingiverse.com/thing:4384974

### Videos how it works
- https://youtu.be/jB6eqvVFAuU<br>
- https://youtu.be/hk_zi0FvA-Q<br>
- https://youtu.be/VRdHTHkP-H8<br>

### Software requirements
- **2019-07-10-raspbian-buster-lite** is used as OS Linux distribution. I assume it should work on any newer(and previous as well) versions, but haven't tested it.<br>
- **ALSA** is used for sound subsystem.<br>
- **[Pocketsphinx](https://github.com/cmusphinx/pocketsphinx)** is the core of the speech recognition. **[Sphinxbase](https://github.com/cmusphinx/sphinxbase)** must be installed for pocketsphinx to work. I compiled both from the sources.<br>
- **CMU Flite** and **eSpeak** are used for Text to Speech purposes(Flite for English and eSpeak for Russian).<br>
- To control the backlight **[NeoPixel library](https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel)** must be installed(with all its dependencies).<br>
- **[Music Player Daemon (MPD)](https://www.musicpd.org/)** is the underlying music player(only to play the music, Bender's answers are playing with **aplay** utility from the ALSA package).

