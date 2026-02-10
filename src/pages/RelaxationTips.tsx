import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Wind, Brain, Clock, Droplets, Move, Heart } from "lucide-react";

const RelaxationTips = () => {
  const [breathPhase, setBreathPhase] = useState<"inhale" | "hold" | "exhale">("inhale");
  const [breathTimer, setBreathTimer] = useState(4);
  const [isBreathing, setIsBreathing] = useState(false);

  useEffect(() => {
    if (!isBreathing) return;
    const interval = setInterval(() => {
      setBreathTimer((prev) => {
        if (prev <= 1) {
          setBreathPhase((p) => (p === "inhale" ? "hold" : p === "hold" ? "exhale" : "inhale"));
          return 4;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [isBreathing]);

  const breathColor = breathPhase === "inhale" ? "from-primary to-secondary" : breathPhase === "hold" ? "from-accent to-primary" : "from-secondary to-primary";

  const mindfulnessTips = [
    { icon: Heart, title: "You are enough", desc: "Take a moment to acknowledge your feelings without judgment. Every emotion is valid." },
    { icon: Brain, title: "Stay Present", desc: "Focus on what you can control right now. Let go of worries about the past or future." },
    { icon: Wind, title: "Release Tension", desc: "Scan your body from head to toe. Notice where you hold tension and consciously relax those areas." },
  ];

  const breakReminders = [
    { icon: Clock, text: "Take a short break every 25 minutes", color: "bg-primary/10 text-primary" },
    { icon: Droplets, text: "Drink a glass of water", color: "bg-accent/10 text-accent-foreground" },
    { icon: Move, text: "Stretch for 2 minutes", color: "bg-secondary/10 text-secondary" },
    { icon: Wind, text: "Step outside for fresh air", color: "bg-primary/10 text-primary" },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="pt-24 pb-16">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4 font-display">
              Relaxation <span className="text-gradient">Tips</span>
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Manage stress with breathing exercises, mindfulness tips, and wellness reminders.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* Breathing Exercise */}
            <div className="lg:col-span-1 rounded-2xl border border-border/50 bg-card p-8 text-center">
              <h3 className="font-display font-bold text-xl mb-6">🌬 Breathing Exercise</h3>
              <div className="relative mb-6">
                <div
                  className={`w-40 h-40 mx-auto rounded-full bg-gradient-to-br ${breathColor} flex items-center justify-center transition-all duration-1000 ${
                    isBreathing
                      ? breathPhase === "inhale"
                        ? "scale-110"
                        : breathPhase === "exhale"
                        ? "scale-90"
                        : "scale-100"
                      : "scale-100"
                  }`}
                  style={{ boxShadow: isBreathing ? "0 0 60px -10px hsl(var(--primary) / 0.4)" : undefined }}
                >
                  <div className="text-center text-primary-foreground">
                    <p className="text-3xl font-bold font-display">{isBreathing ? breathTimer : "—"}</p>
                    <p className="text-sm font-medium capitalize">{isBreathing ? breathPhase : "Ready"}</p>
                  </div>
                </div>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                Inhale 4 sec → Hold 4 sec → Exhale 4 sec
              </p>
              <button
                onClick={() => { setIsBreathing(!isBreathing); setBreathPhase("inhale"); setBreathTimer(4); }}
                className={`px-8 py-3 rounded-full font-display font-semibold text-sm transition-all ${
                  isBreathing
                    ? "bg-destructive/10 text-destructive border border-destructive/30"
                    : "gradient-primary text-primary-foreground shadow-glow"
                }`}
              >
                {isBreathing ? "Stop" : "Start Breathing"}
              </button>
            </div>

            {/* Mindfulness Tips */}
            <div className="lg:col-span-1 space-y-4">
              <h3 className="font-display font-bold text-xl mb-4">🧘 Mindfulness Tips</h3>
              {mindfulnessTips.map((tip, i) => (
                <div
                  key={i}
                  className="rounded-2xl border border-border/50 bg-card p-6 hover:shadow-soft transition-all duration-300 animate-fade-in"
                  style={{ animationDelay: `${i * 0.15}s` }}
                >
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 rounded-xl gradient-primary flex items-center justify-center shrink-0">
                      <tip.icon className="h-5 w-5 text-primary-foreground" />
                    </div>
                    <div>
                      <h4 className="font-display font-semibold mb-1">{tip.title}</h4>
                      <p className="text-sm text-muted-foreground leading-relaxed">{tip.desc}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Break Reminders */}
            <div className="lg:col-span-1 space-y-4">
              <h3 className="font-display font-bold text-xl mb-4">⏰ Break Reminders</h3>
              {breakReminders.map((rem, i) => (
                <div
                  key={i}
                  className="rounded-2xl border border-border/50 bg-card p-5 flex items-center gap-4 hover:shadow-soft transition-all duration-300 animate-fade-in"
                  style={{ animationDelay: `${i * 0.1}s` }}
                >
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${rem.color}`}>
                    <rem.icon className="h-6 w-6" />
                  </div>
                  <p className="font-medium text-sm">{rem.text}</p>
                </div>
              ))}

              {/* Quick tip card */}
              <div className="rounded-2xl gradient-primary p-6 text-primary-foreground mt-6">
                <h4 className="font-display font-bold text-lg mb-2">💡 Quick Tip</h4>
                <p className="text-sm text-primary-foreground/80 leading-relaxed">
                  Regular short breaks improve focus by 30%. Use the Pomodoro technique: 
                  25 minutes work, 5 minutes rest.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default RelaxationTips;
