import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import FeaturesSection from "@/components/FeaturesSection";
import HowItWorksSection from "@/components/HowItWorksSection";
import TechSection from "@/components/TechSection";
import Footer from "@/components/Footer";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <HeroSection />
      
      {/* Project Overview */}
      <section className="py-20">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4 font-display">
            Project <span className="text-gradient">Overview</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-3xl mx-auto mb-6 leading-relaxed">
            In today's fast-paced world, stress and emotional imbalance are growing concerns. Our system uses 
            <strong> NLP, Machine Learning, and Computer Vision</strong> to detect emotions from text, voice, and facial expressions, 
            then recommends personalized music and wellness activities to help users manage stress effectively.
          </p>
          <Link to="/analyze">
            <Button size="lg" className="gradient-primary text-primary-foreground rounded-full px-8">
              Start Emotion Analysis <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>

      <FeaturesSection />
      <HowItWorksSection />
      <TechSection />
      <Footer />
    </div>
  );
};

export default Index;
