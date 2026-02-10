import { Brain, Music, Activity, Shield, BarChart3, Sparkles } from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "Emotion Detection",
    description: "Advanced AI analyzes facial expressions and physiological signals to accurately detect your emotional state in real-time.",
  },
  {
    icon: Music,
    title: "Music Therapy",
    description: "Curated playlists tailored to your mood, leveraging music psychology to help regulate emotions and reduce stress.",
  },
  {
    icon: Activity,
    title: "Activity Suggestions",
    description: "Personalized wellness activities including meditation, breathing exercises, and physical activities based on your stress levels.",
  },
  {
    icon: BarChart3,
    title: "Stress Analytics",
    description: "Track your emotional patterns over time with insightful visualizations and progress reports.",
  },
  {
    icon: Shield,
    title: "Privacy First",
    description: "All emotion data is processed locally and encrypted. Your mental health data stays private and secure.",
  },
  {
    icon: Sparkles,
    title: "Adaptive Learning",
    description: "The system learns from your preferences and feedback to deliver increasingly accurate recommendations.",
  },
];

const FeaturesSection = () => {
  return (
    <section className="py-24 bg-muted/30">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
            Intelligent <span className="text-gradient">Features</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-xl mx-auto">
            A comprehensive system designed to understand and improve your emotional well-being.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
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
