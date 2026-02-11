import { useState } from "react";
import { Music, Dumbbell, BookOpen, Wind } from "lucide-react";

const moods = [
  { emoji: "😊", label: "Happy", color: "bg-accent/20 border-accent/40 hover:border-accent" },
  { emoji: "😔", label: "Sad", color: "bg-secondary/20 border-secondary/40 hover:border-secondary" },
  { emoji: "😰", label: "Stressed", color: "bg-destructive/10 border-destructive/30 hover:border-destructive" },
  { emoji: "😌", label: "Calm", color: "bg-primary/10 border-primary/30 hover:border-primary" },
  { emoji: "😤", label: "Angry", color: "bg-destructive/15 border-destructive/30 hover:border-destructive" },
  { emoji: "🥱", label: "Tired", color: "bg-muted border-border hover:border-muted-foreground" },
];

const recommendations: Record<string, { music: string; activity: string; exercise: string; breathing: string }> = {
  Happy: { music: "Upbeat Pop & Dance", activity: "Social Activities", exercise: "Dancing or Jogging", breathing: "Energizing Breath" },
  Sad: { music: "Soothing Acoustic", activity: "Journaling", exercise: "Gentle Yoga", breathing: "Deep Breathing" },
  Stressed: { music: "Lo-fi & Ambient", activity: "Meditation", exercise: "Stretching", breathing: "Box Breathing" },
  Calm: { music: "Classical Piano", activity: "Reading", exercise: "Nature Walk", breathing: "Mindful Breathing" },
  Angry: { music: "Instrumental Rock", activity: "Art Therapy", exercise: "Intense Workout", breathing: "4-7-8 Technique" },
  Tired: { music: "Chill Electronic", activity: "Power Nap", exercise: "Light Stretching", breathing: "Relaxation Breath" },
};

const recIcons = [
  { key: "music" as const, icon: Music, label: "Music" },
  { key: "activity" as const, icon: BookOpen, label: "Activity" },
  { key: "exercise" as const, icon: Dumbbell, label: "Exercise" },
  { key: "breathing" as const, icon: Wind, label: "Breathing" },
];

const MoodSelector = () => {
  const [selected, setSelected] = useState<string | null>(null);
  const rec = selected ? recommendations[selected] : null;

  return (
    <section className="py-24 bg-muted/30">
      <div className="container mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
            How Are You <span className="text-gradient">Feeling</span>?
          </h2>
          <p className="text-lg text-muted-foreground max-w-xl mx-auto">
            Select your current mood and get instant recommendations.
          </p>
        </div>

        {/* Mood Grid */}
        <div className="flex flex-wrap justify-center gap-4 mb-12">
          {moods.map((mood) => (
            <button
              key={mood.label}
              onClick={() => setSelected(mood.label)}
              className={`flex flex-col items-center gap-2 rounded-2xl border-2 px-8 py-6 transition-all duration-300 hover:-translate-y-1 ${mood.color} ${
                selected === mood.label ? "ring-2 ring-primary scale-105 shadow-soft" : ""
              }`}
            >
              <span className="text-4xl">{mood.emoji}</span>
              <span className="text-sm font-semibold font-display">{mood.label}</span>
            </button>
          ))}
        </div>

        {/* Recommendation Cards */}
        {rec && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-4xl mx-auto animate-fade-in">
            {recIcons.map(({ key, icon: Icon, label }) => (
              <div key={key} className="rounded-xl border border-border/50 bg-card p-6 text-center shadow-soft">
                <div className="w-10 h-10 rounded-lg gradient-primary flex items-center justify-center mx-auto mb-3">
                  <Icon className="h-5 w-5 text-primary-foreground" />
                </div>
                <p className="text-xs text-muted-foreground mb-1">{label}</p>
                <p className="font-semibold font-display text-sm">{rec[key]}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
};

export default MoodSelector;
