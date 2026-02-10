import { Brain } from "lucide-react";
import { Link } from "react-router-dom";

const Footer = () => (
  <footer className="py-12 border-t border-border/50 bg-muted/30">
    <div className="container mx-auto px-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-lg gradient-primary flex items-center justify-center">
              <Brain className="h-4 w-4 text-primary-foreground" />
            </div>
            <span className="font-display font-bold text-lg">MoodSync</span>
          </div>
          <p className="text-sm text-muted-foreground leading-relaxed">
            Smart Music & Activity Recommendation System for Emotion and Stress Management
          </p>
        </div>

        <div>
          <h4 className="font-display font-semibold mb-3">Quick Links</h4>
          <div className="space-y-2">
            {[
              { label: "Analyze Emotion", path: "/analyze" },
              { label: "Music", path: "/music" },
              { label: "Relaxation Tips", path: "/relaxation" },
              { label: "About Project", path: "/about" },
            ].map((l) => (
              <Link key={l.path} to={l.path} className="block text-sm text-muted-foreground hover:text-primary transition-colors">
                {l.label}
              </Link>
            ))}
          </div>
        </div>

        <div>
          <h4 className="font-display font-semibold mb-3">Technologies Used</h4>
          <div className="flex flex-wrap gap-2">
            {["Python", "Flask", "NLP", "Machine Learning", "OpenCV", "HTML/CSS/JS", "React"].map((t) => (
              <span key={t} className="text-xs px-3 py-1 rounded-full bg-primary/10 text-primary font-medium">
                {t}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="border-t border-border/50 pt-6 flex flex-col sm:flex-row items-center justify-between gap-2">
        <p className="text-xs text-muted-foreground">
          Academic Project – For Educational Use Only | © {new Date().getFullYear()}
        </p>
        <p className="text-xs text-muted-foreground">
          Final Year Project – Computer Science Department
        </p>
      </div>
    </div>
  </footer>
);

export default Footer;
