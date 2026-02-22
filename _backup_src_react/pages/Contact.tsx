import { useState } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Send, CheckCircle, Mail, MessageSquare, User } from "lucide-react";

const Contact = () => {
  const [submitted, setSubmitted] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", message: "" });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="pt-24 pb-16">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4 font-display">
              Contact & <span className="text-gradient">Feedback</span>
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Share your thoughts, feedback, or questions about the project.
            </p>
          </div>

          <div className="max-w-xl mx-auto">
            {submitted ? (
              <div className="rounded-2xl border border-primary/20 bg-primary/5 p-12 text-center animate-scale-in">
                <CheckCircle className="h-16 w-16 text-primary mx-auto mb-4" />
                <h2 className="font-display font-bold text-2xl mb-2">Thank You!</h2>
                <p className="text-muted-foreground mb-6">
                  Your feedback has been received. We appreciate your input!
                </p>
                <Button
                  onClick={() => { setSubmitted(false); setForm({ name: "", email: "", message: "" }); }}
                  variant="outline"
                  className="rounded-full"
                >
                  Send Another
                </Button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="rounded-2xl border border-border/50 bg-card p-8 space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="name" className="font-display font-semibold flex items-center gap-2">
                    <User className="h-4 w-4 text-primary" /> Name
                  </Label>
                  <Input
                    id="name"
                    placeholder="Your full name"
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                    required
                    className="rounded-xl"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email" className="font-display font-semibold flex items-center gap-2">
                    <Mail className="h-4 w-4 text-primary" /> Email
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="your@email.com"
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                    required
                    className="rounded-xl"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="message" className="font-display font-semibold flex items-center gap-2">
                    <MessageSquare className="h-4 w-4 text-primary" /> Feedback / Message
                  </Label>
                  <Textarea
                    id="message"
                    placeholder="Share your thoughts, suggestions, or questions..."
                    value={form.message}
                    onChange={(e) => setForm({ ...form, message: e.target.value })}
                    required
                    className="min-h-[120px] rounded-xl resize-none"
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full gradient-primary text-primary-foreground rounded-full py-6 text-lg font-display"
                >
                  <Send className="h-5 w-5 mr-2" />
                  Submit Feedback
                </Button>
              </form>
            )}
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default Contact;
