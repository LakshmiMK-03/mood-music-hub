import { Brain } from "lucide-react";

const Footer = () => (
  <footer className="py-12 border-t border-border/50">
    <div className="container mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-lg gradient-primary flex items-center justify-center">
          <Brain className="h-4 w-4 text-primary-foreground" />
        </div>
        <span className="font-display font-bold text-lg">MoodSync</span>
      </div>
      <p className="text-sm text-muted-foreground">
        Final Year Project — Smart Music & Activity Recommendation System
      </p>
    </div>
  </footer>
);

export default Footer;
