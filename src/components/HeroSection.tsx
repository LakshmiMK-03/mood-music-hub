import { ArrowRight, Brain, Music, Heart } from "lucide-react";
import { Button } from "@/components/ui/button";
import heroBg from "@/assets/hero-bg.jpg";

const HeroSection = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background image with overlay */}
      <div className="absolute inset-0">
        <img src={heroBg} alt="" className="w-full h-full object-cover" />
        <div className="absolute inset-0 bg-background/70 backdrop-blur-sm" />
      </div>

      <div className="relative z-10 container mx-auto px-6 py-20 text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-2 mb-8 animate-fade-in">
          <Brain className="h-4 w-4 text-primary" />
          <span className="text-sm font-medium text-primary">AI-Powered Wellness</span>
        </div>

        {/* Heading */}
        <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold tracking-tight mb-6 animate-fade-in" style={{ animationDelay: "0.1s" }}>
          Smart Music &{" "}
          <span className="text-gradient">Activity</span>
          <br />
          Recommendation System
        </h1>

        <p className="max-w-2xl mx-auto text-lg sm:text-xl text-muted-foreground mb-10 animate-fade-in" style={{ animationDelay: "0.2s" }}>
          Harness the power of emotion detection and AI to manage stress through personalized music and activity recommendations.
        </p>

        {/* CTA buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in" style={{ animationDelay: "0.3s" }}>
          <Button size="lg" className="gradient-primary text-primary-foreground px-8 py-6 text-lg rounded-full shadow-glow hover:opacity-90 transition-opacity">
            Get Started <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
          <Button size="lg" variant="outline" className="px-8 py-6 text-lg rounded-full border-primary/30 hover:bg-primary/5">
            Learn More
          </Button>
        </div>

        {/* Floating icons */}
        <div className="mt-16 flex justify-center gap-12 animate-fade-in" style={{ animationDelay: "0.5s" }}>
          <div className="animate-float" style={{ animationDelay: "0s" }}>
            <div className="w-16 h-16 rounded-2xl gradient-primary flex items-center justify-center shadow-glow">
              <Music className="h-8 w-8 text-primary-foreground" />
            </div>
          </div>
          <div className="animate-float" style={{ animationDelay: "2s" }}>
            <div className="w-16 h-16 rounded-2xl bg-secondary flex items-center justify-center shadow-soft">
              <Brain className="h-8 w-8 text-secondary-foreground" />
            </div>
          </div>
          <div className="animate-float" style={{ animationDelay: "4s" }}>
            <div className="w-16 h-16 rounded-2xl bg-accent flex items-center justify-center shadow-soft">
              <Heart className="h-8 w-8 text-accent-foreground" />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
