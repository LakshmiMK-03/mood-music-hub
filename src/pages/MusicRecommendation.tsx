import { useState } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Play, Pause, SkipForward, SkipBack, Volume2, Music } from "lucide-react";
import { Slider } from "@/components/ui/slider";

const emotionPlaylists: Record<string, { name: string; songs: { title: string; artist: string; duration: string }[] }> = {
  Sad: {
    name: "Calm & Peaceful – For Stress Relief",
    songs: [
      { title: "Weightless", artist: "Marconi Union", duration: "3:45" },
      { title: "Clair de Lune", artist: "Debussy", duration: "5:12" },
      { title: "Gymnopédie No.1", artist: "Erik Satie", duration: "3:20" },
      { title: "River Flows in You", artist: "Yiruma", duration: "4:02" },
      { title: "Sunset Lover", artist: "Petit Biscuit", duration: "3:58" },
    ],
  },
  Angry: {
    name: "Soothing Instrumentals – Cool Down",
    songs: [
      { title: "Adagio for Strings", artist: "Samuel Barber", duration: "7:24" },
      { title: "Nocturne Op.9 No.2", artist: "Chopin", duration: "4:33" },
      { title: "Moonlight Sonata", artist: "Beethoven", duration: "6:10" },
      { title: "Canon in D", artist: "Pachelbel", duration: "5:15" },
      { title: "The Swan", artist: "Saint-Saëns", duration: "3:20" },
    ],
  },
  Happy: {
    name: "Energetic Vibes – Keep the Joy",
    songs: [
      { title: "Happy", artist: "Pharrell Williams", duration: "3:53" },
      { title: "Walking on Sunshine", artist: "Katrina & The Waves", duration: "3:58" },
      { title: "Good Vibrations", artist: "The Beach Boys", duration: "3:36" },
      { title: "Uptown Funk", artist: "Bruno Mars", duration: "4:30" },
      { title: "Can't Stop the Feeling!", artist: "Justin Timberlake", duration: "4:00" },
    ],
  },
  Neutral: {
    name: "Lo-fi Focus – Stay Balanced",
    songs: [
      { title: "Snowman", artist: "WYS", duration: "2:50" },
      { title: "Coffee", artist: "beabadoobee", duration: "3:28" },
      { title: "Affection", artist: "Jinsang", duration: "2:15" },
      { title: "Biscuit Town", artist: "King Krule", duration: "4:12" },
      { title: "Windows", artist: "Jhove", duration: "3:00" },
    ],
  },
};

const emotionMusicMap = [
  { emotion: "😟 Sad", music: "Calm & Soothing", genre: "Acoustic, Piano, Lo-fi" },
  { emotion: "😤 Angry", music: "Instrumental & Classical", genre: "Classical, Ambient" },
  { emotion: "😊 Happy", music: "Energetic & Upbeat", genre: "Pop, Dance, Rock" },
  { emotion: "😐 Neutral", music: "Lo-fi & Focus", genre: "Lo-fi, Chill, Jazz" },
  { emotion: "😨 Fearful", music: "Grounding & Warm", genre: "Nature Sounds, Acoustic" },
  { emotion: "😲 Surprised", music: "Exploratory & New", genre: "World, Electronic" },
];

const MusicRecommendation = () => {
  const [selectedEmotion, setSelectedEmotion] = useState("Sad");
  const [playing, setPlaying] = useState(false);
  const [currentSong, setCurrentSong] = useState(0);
  const [volume, setVolume] = useState([75]);

  const playlist = emotionPlaylists[selectedEmotion];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="pt-24 pb-16">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4 font-display">
              Music <span className="text-gradient">Recommendations</span>
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Personalized playlists based on your detected emotion. Select an emotion to explore.
            </p>
          </div>

          {/* Emotion Selector */}
          <div className="flex flex-wrap justify-center gap-3 mb-10">
            {Object.keys(emotionPlaylists).map((emotion) => (
              <button
                key={emotion}
                onClick={() => { setSelectedEmotion(emotion); setCurrentSong(0); setPlaying(false); }}
                className={`px-6 py-3 rounded-full font-display font-semibold text-sm transition-all duration-300 ${
                  selectedEmotion === emotion
                    ? "gradient-primary text-primary-foreground shadow-glow scale-105"
                    : "bg-muted text-muted-foreground hover:bg-muted/80"
                }`}
              >
                {emotion}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {/* Playlist */}
            <div className="rounded-2xl border border-border/50 bg-card overflow-hidden">
              <div className="gradient-primary p-6">
                <div className="flex items-center gap-3">
                  <Music className="h-6 w-6 text-primary-foreground" />
                  <div>
                    <p className="text-primary-foreground/70 text-sm">Recommended Playlist</p>
                    <h3 className="font-display font-bold text-lg text-primary-foreground">{playlist.name}</h3>
                  </div>
                </div>
                <span className="inline-block mt-3 text-xs px-3 py-1 rounded-full bg-primary-foreground/20 text-primary-foreground">
                  Emotion: {selectedEmotion}
                </span>
              </div>
              <div className="divide-y divide-border/30">
                {playlist.songs.map((song, i) => (
                  <button
                    key={i}
                    onClick={() => { setCurrentSong(i); setPlaying(true); }}
                    className={`w-full flex items-center gap-4 p-4 hover:bg-muted/50 transition-colors text-left ${
                      currentSong === i ? "bg-primary/5" : ""
                    }`}
                  >
                    <span className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-display font-bold ${
                      currentSong === i ? "gradient-primary text-primary-foreground" : "bg-muted text-muted-foreground"
                    }`}>
                      {currentSong === i && playing ? "▶" : i + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className={`font-medium text-sm truncate ${currentSong === i ? "text-primary" : ""}`}>
                        {song.title}
                      </p>
                      <p className="text-xs text-muted-foreground">{song.artist}</p>
                    </div>
                    <span className="text-xs text-muted-foreground">{song.duration}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Player & Mapping */}
            <div className="space-y-6">
              {/* Music Player */}
              <div className="rounded-2xl border border-border/50 bg-card p-6">
                <h3 className="font-display font-bold text-lg mb-4">🎧 Now Playing</h3>
                <div className="text-center mb-6">
                  <div className="w-32 h-32 rounded-2xl gradient-primary mx-auto flex items-center justify-center mb-4 shadow-glow">
                    <Music className="h-16 w-16 text-primary-foreground" />
                  </div>
                  <p className="font-display font-bold">{playlist.songs[currentSong].title}</p>
                  <p className="text-sm text-muted-foreground">{playlist.songs[currentSong].artist}</p>
                </div>

                {/* Progress bar */}
                <div className="mb-4">
                  <Slider defaultValue={[35]} max={100} step={1} className="mb-2" />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>1:23</span>
                    <span>{playlist.songs[currentSong].duration}</span>
                  </div>
                </div>

                {/* Controls */}
                <div className="flex items-center justify-center gap-6">
                  <button onClick={() => setCurrentSong(Math.max(0, currentSong - 1))} className="p-2 hover:bg-muted rounded-full transition-colors">
                    <SkipBack className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => setPlaying(!playing)}
                    className="w-14 h-14 rounded-full gradient-primary flex items-center justify-center shadow-glow hover:opacity-90 transition-opacity"
                  >
                    {playing ? <Pause className="h-6 w-6 text-primary-foreground" /> : <Play className="h-6 w-6 text-primary-foreground ml-0.5" />}
                  </button>
                  <button onClick={() => setCurrentSong(Math.min(playlist.songs.length - 1, currentSong + 1))} className="p-2 hover:bg-muted rounded-full transition-colors">
                    <SkipForward className="h-5 w-5" />
                  </button>
                </div>

                {/* Volume */}
                <div className="flex items-center gap-3 mt-4">
                  <Volume2 className="h-4 w-4 text-muted-foreground" />
                  <Slider value={volume} onValueChange={setVolume} max={100} step={1} className="flex-1" />
                </div>
              </div>

              {/* Emotion ↔ Music Mapping */}
              <div className="rounded-2xl border border-border/50 bg-card p-6">
                <h3 className="font-display font-bold text-lg mb-4">🔁 Emotion ↔ Music Mapping</h3>
                <div className="space-y-3">
                  {emotionMusicMap.map((row) => (
                    <div key={row.emotion} className="flex items-center gap-3 p-3 rounded-xl bg-muted/30 hover:bg-muted/50 transition-colors">
                      <span className="text-lg w-10">{row.emotion.split(" ")[0]}</span>
                      <div className="flex-1">
                        <p className="font-medium text-sm">{row.emotion.split(" ")[1]} → {row.music}</p>
                        <p className="text-xs text-muted-foreground">{row.genre}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default MusicRecommendation;
