import { Code, Database, Eye, Brain, Globe, Cpu } from "lucide-react";

const techs = [
  { icon: Code, name: "Python", desc: "Core backend language" },
  { icon: Globe, name: "Flask", desc: "Web framework" },
  { icon: Brain, name: "NLP", desc: "Natural Language Processing" },
  { icon: Cpu, name: "Machine Learning", desc: "Emotion & stress prediction" },
  { icon: Eye, name: "OpenCV", desc: "Face emotion detection" },
  { icon: Database, name: "HTML/CSS/JS", desc: "Frontend technologies" },
];

const TechSection = () => (
  <section className="py-24">
    <div className="container mx-auto px-6 text-center">
      <h2 className="text-3xl sm:text-4xl font-bold mb-4 font-display">
        Technologies <span className="text-gradient">Used</span>
      </h2>
      <p className="text-lg text-muted-foreground max-w-xl mx-auto mb-12">
        Built with industry-standard tools for reliable emotion detection and recommendations.
      </p>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-6">
        {techs.map((t, i) => (
          <div
            key={t.name}
            className="flex flex-col items-center gap-3 p-6 rounded-2xl border border-border/50 bg-card hover:shadow-soft hover:-translate-y-1 transition-all duration-300 animate-fade-in"
            style={{ animationDelay: `${i * 0.1}s` }}
          >
            <div className="w-14 h-14 rounded-xl gradient-primary flex items-center justify-center">
              <t.icon className="h-7 w-7 text-primary-foreground" />
            </div>
            <span className="font-display font-semibold text-sm">{t.name}</span>
            <span className="text-xs text-muted-foreground">{t.desc}</span>
          </div>
        ))}
      </div>
    </div>
  </section>
);

export default TechSection;
