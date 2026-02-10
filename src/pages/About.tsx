import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Brain, Target, Cpu, Music, Eye, Code, Database, Globe, BarChart3, Shield } from "lucide-react";

const objectives = [
  "Detect emotions from text, voice, and facial expressions using AI",
  "Predict stress levels based on emotional analysis",
  "Recommend personalized music playlists to improve mood",
  "Provide relaxation tips and wellness activities for stress management",
];

const modules = [
  { icon: Code, name: "NLP Module", desc: "Processes text input using natural language processing to identify emotional keywords and sentiment." },
  { icon: Brain, name: "Emotion Detection", desc: "Uses machine learning classifiers to categorize emotions from multiple input sources." },
  { icon: BarChart3, name: "Stress Analysis", desc: "Evaluates stress levels (Low/Medium/High) based on detected emotional patterns." },
  { icon: Music, name: "Music Recommendation", desc: "Maps detected emotions to curated playlists using emotion-music psychology models." },
];

const techStack = [
  { icon: Code, name: "Python", category: "Backend" },
  { icon: Globe, name: "Flask", category: "Web Framework" },
  { icon: Brain, name: "NLP (NLTK/SpaCy)", category: "Text Processing" },
  { icon: Cpu, name: "Scikit-learn / TensorFlow", category: "Machine Learning" },
  { icon: Eye, name: "OpenCV", category: "Computer Vision" },
  { icon: Database, name: "HTML / CSS / JavaScript", category: "Frontend" },
  { icon: Shield, name: "React + Tailwind CSS", category: "UI Framework" },
];

const About = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="pt-24 pb-16">
        <div className="container mx-auto px-6">
          {/* Header */}
          <div className="text-center mb-16">
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4 font-display">
              About the <span className="text-gradient">Project</span>
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              A comprehensive overview of the Smart Music & Activity Recommendation System for Emotion and Stress Management.
            </p>
          </div>

          <div className="max-w-5xl mx-auto space-y-16">
            {/* Problem & Solution */}
            <section className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="rounded-2xl border border-border/50 bg-card p-8">
                <h2 className="font-display font-bold text-2xl mb-4 flex items-center gap-3">
                  <span className="w-10 h-10 rounded-xl bg-destructive/10 flex items-center justify-center">📌</span>
                  Problem Statement
                </h2>
                <p className="text-muted-foreground leading-relaxed">
                  In today's high-pressure academic and professional environments, students and individuals face 
                  increasing levels of stress, anxiety, and emotional distress. Traditional stress management tools 
                  are often generic, requiring manual input, and fail to provide personalized, real-time solutions 
                  based on the user's actual emotional state.
                </p>
              </div>
              <div className="rounded-2xl border border-primary/20 bg-primary/5 p-8">
                <h2 className="font-display font-bold text-2xl mb-4 flex items-center gap-3">
                  <span className="w-10 h-10 rounded-xl gradient-primary flex items-center justify-center text-primary-foreground">💡</span>
                  Proposed Solution
                </h2>
                <p className="text-muted-foreground leading-relaxed">
                  This system uses <strong>NLP, Machine Learning, and Computer Vision</strong> to automatically detect 
                  emotions from text, voice, and facial expressions. It then provides personalized music recommendations 
                  and relaxation activities based on the detected emotion and stress level, enabling real-time emotional 
                  wellness support.
                </p>
              </div>
            </section>

            {/* Objectives */}
            <section>
              <h2 className="font-display font-bold text-2xl mb-6 flex items-center gap-3">
                <Target className="h-6 w-6 text-primary" />
                Objectives
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {objectives.map((obj, i) => (
                  <div key={i} className="flex items-start gap-3 p-4 rounded-xl border border-border/50 bg-card animate-fade-in" style={{ animationDelay: `${i * 0.1}s` }}>
                    <span className="w-8 h-8 rounded-lg gradient-primary flex items-center justify-center text-primary-foreground text-sm font-bold shrink-0 font-display">
                      {i + 1}
                    </span>
                    <p className="text-sm leading-relaxed">{obj}</p>
                  </div>
                ))}
              </div>
            </section>

            {/* Modules */}
            <section>
              <h2 className="font-display font-bold text-2xl mb-6 flex items-center gap-3">
                <Cpu className="h-6 w-6 text-primary" />
                System Modules
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {modules.map((mod, i) => (
                  <div key={i} className="rounded-2xl border border-border/50 bg-card p-6 hover:shadow-soft transition-all duration-300 animate-fade-in" style={{ animationDelay: `${i * 0.1}s` }}>
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 rounded-xl gradient-primary flex items-center justify-center shrink-0">
                        <mod.icon className="h-6 w-6 text-primary-foreground" />
                      </div>
                      <div>
                        <h3 className="font-display font-semibold text-lg mb-1">{mod.name}</h3>
                        <p className="text-sm text-muted-foreground leading-relaxed">{mod.desc}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Tech Stack */}
            <section>
              <h2 className="font-display font-bold text-2xl mb-6 flex items-center gap-3">
                <Code className="h-6 w-6 text-primary" />
                Technology Stack
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                {techStack.map((tech, i) => (
                  <div key={i} className="rounded-2xl border border-border/50 bg-card p-5 text-center hover:shadow-soft hover:-translate-y-1 transition-all duration-300 animate-fade-in" style={{ animationDelay: `${i * 0.08}s` }}>
                    <div className="w-12 h-12 rounded-xl gradient-primary flex items-center justify-center mx-auto mb-3">
                      <tech.icon className="h-6 w-6 text-primary-foreground" />
                    </div>
                    <p className="font-display font-semibold text-sm">{tech.name}</p>
                    <p className="text-xs text-muted-foreground">{tech.category}</p>
                  </div>
                ))}
              </div>
            </section>

            {/* Examiner-friendly summary */}
            <section className="rounded-2xl gradient-primary p-8 text-primary-foreground">
              <h3 className="font-display font-bold text-xl mb-3">📝 Project Summary</h3>
              <p className="text-primary-foreground/90 leading-relaxed">
                "The frontend is designed as a user-friendly web application that allows users to input text, voice, 
                or images, displays detected emotions and stress levels, and provides personalized music recommendations 
                and relaxation tips in real time."
              </p>
            </section>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default About;
