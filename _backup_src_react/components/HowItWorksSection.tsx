import { ScanFace, Cpu, Headphones, TrendingUp } from "lucide-react";

const steps = [
  {
    icon: ScanFace,
    step: "01",
    title: "Detect Emotion",
    description: "The system captures your emotional state through facial analysis or manual input.",
  },
  {
    icon: Cpu,
    step: "02",
    title: "AI Processing",
    description: "Our machine learning model processes the data and identifies stress patterns and emotional context.",
  },
  {
    icon: Headphones,
    step: "03",
    title: "Get Recommendations",
    description: "Receive personalized music playlists and wellness activities tailored to your current state.",
  },
  {
    icon: TrendingUp,
    step: "04",
    title: "Track Progress",
    description: "Monitor your emotional well-being over time and see how recommendations improve your mood.",
  },
];

const HowItWorksSection = () => {
  return (
    <section className="py-24">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
            How It <span className="text-gradient">Works</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-xl mx-auto">
            Four simple steps to better emotional well-being.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <div key={step.step} className="relative text-center animate-fade-in" style={{ animationDelay: `${index * 0.15}s` }}>
              {/* Connector line */}
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-10 left-[60%] w-[80%] h-[2px] bg-gradient-to-r from-primary/30 to-primary/5" />
              )}

              <div className="relative inline-flex items-center justify-center w-20 h-20 rounded-full gradient-primary mb-6 shadow-glow">
                <step.icon className="h-8 w-8 text-primary-foreground" />
                <span className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-accent text-accent-foreground text-sm font-bold flex items-center justify-center font-display">
                  {step.step}
                </span>
              </div>
              <h3 className="text-xl font-semibold mb-3 font-display">{step.title}</h3>
              <p className="text-muted-foreground leading-relaxed">{step.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;
