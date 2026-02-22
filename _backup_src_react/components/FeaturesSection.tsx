import { Brain, Music, Activity, BarChart3, BookOpen, Wind } from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "Emotion Detection",
    description: "AI analyzes facial expressions, text sentiment, and voice to accurately detect your emotional state in real-time.",
  },
  {
    icon: BarChart3,
    title: "Stress Analysis",
    description: "Evaluates your stress level (Low / Medium / High) based on detected emotional patterns and intensity.",
  },
  {
    icon: Music,
    title: "Music Recommendation",
    description: "Curated playlists tailored to your mood — calm music for stress, energetic tracks for happiness.",
  },
  {
    icon: Wind,
    title: "Relaxation Tips",
    description: "Breathing exercises, mindfulness tips, and break reminders to help manage stress effectively.",
  },
];

const FeaturesSection = () => {
  return (
    <section className="py-24 bg-muted/30">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4 font-display">
            Key <span className="text-gradient">Features</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-xl mx-auto">
            A comprehensive system designed to understand and improve your emotional well-being.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <div
              key={feature.title}
              className="group relative rounded-2xl border border-border/50 bg-card p-8 transition-all duration-300 hover:shadow-soft hover:-translate-y-1 hover:border-primary/20 animate-fade-in"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="w-12 h-12 rounded-xl gradient-primary flex items-center justify-center mb-5 group-hover:shadow-glow transition-shadow duration-300">
                <feature.icon className="h-6 w-6 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold mb-3 font-display">{feature.title}</h3>
              <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
