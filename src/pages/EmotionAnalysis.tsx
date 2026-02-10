import { useState } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Mic, Type, ImageIcon, Loader2, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

const emotions = ["Happy", "Sad", "Angry", "Neutral", "Fearful", "Surprised"] as const;
const stressLevels = ["Low", "Medium", "High"] as const;
const emojis: Record<string, string> = {
  Happy: "😊", Sad: "😟", Angry: "😤", Neutral: "😐", Fearful: "😨", Surprised: "😲",
};
const stressColors: Record<string, string> = {
  Low: "text-primary", Medium: "text-accent", High: "text-destructive",
};

const EmotionAnalysis = () => {
  const [textInput, setTextInput] = useState("");
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<{
    emotion: string;
    stress: string;
    confidence: number;
  } | null>(null);

  const simulateAnalysis = () => {
    setAnalyzing(true);
    setResult(null);
    setTimeout(() => {
      const emotion = emotions[Math.floor(Math.random() * emotions.length)];
      const stress = stressLevels[Math.floor(Math.random() * stressLevels.length)];
      const confidence = Math.floor(Math.random() * 20) + 78;
      setResult({ emotion, stress, confidence });
      setAnalyzing(false);
    }, 2000);
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => setImagePreview(reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="pt-24 pb-16">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4 font-display">
              Emotion <span className="text-gradient">Analysis</span>
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Provide text, voice, or an image — our AI will detect your emotion and stress level.
            </p>
          </div>

          <div className="max-w-3xl mx-auto">
            {/* Input Tabs */}
            <Tabs defaultValue="text" className="mb-10">
              <TabsList className="w-full grid grid-cols-3 h-14 rounded-2xl bg-muted/60 p-1">
                <TabsTrigger value="text" className="rounded-xl gap-2 font-display text-sm data-[state=active]:gradient-primary data-[state=active]:text-primary-foreground">
                  <Type className="h-4 w-4" /> Text Input
                </TabsTrigger>
                <TabsTrigger value="voice" className="rounded-xl gap-2 font-display text-sm data-[state=active]:gradient-primary data-[state=active]:text-primary-foreground">
                  <Mic className="h-4 w-4" /> Voice Input
                </TabsTrigger>
                <TabsTrigger value="image" className="rounded-xl gap-2 font-display text-sm data-[state=active]:gradient-primary data-[state=active]:text-primary-foreground">
                  <ImageIcon className="h-4 w-4" /> Image Input
                </TabsTrigger>
              </TabsList>

              <TabsContent value="text" className="mt-6">
                <div className="rounded-2xl border border-border/50 bg-card p-6 space-y-4">
                  <label className="font-display font-semibold text-lg">How are you feeling today?</label>
                  <Textarea
                    placeholder="Type your thoughts, feelings, or describe your current emotional state..."
                    value={textInput}
                    onChange={(e) => setTextInput(e.target.value)}
                    className="min-h-[120px] rounded-xl resize-none text-base"
                  />
                  <Button
                    onClick={simulateAnalysis}
                    disabled={!textInput.trim() || analyzing}
                    className="gradient-primary text-primary-foreground rounded-full px-8"
                  >
                    {analyzing ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                    Analyze Emotion
                  </Button>
                </div>
              </TabsContent>

              <TabsContent value="voice" className="mt-6">
                <div className="rounded-2xl border border-border/50 bg-card p-8 text-center space-y-6">
                  <div className="flex flex-col items-center gap-4">
                    <button
                      onClick={() => {
                        setIsRecording(!isRecording);
                        if (isRecording) simulateAnalysis();
                      }}
                      className={`w-24 h-24 rounded-full flex items-center justify-center transition-all duration-300 ${
                        isRecording
                          ? "bg-destructive/20 border-4 border-destructive animate-pulse-soft"
                          : "gradient-primary shadow-glow hover:scale-105"
                      }`}
                    >
                      <Mic className={`h-10 w-10 ${isRecording ? "text-destructive" : "text-primary-foreground"}`} />
                    </button>
                    <p className="font-display font-semibold">
                      {isRecording ? "🔴 Recording... Click to stop" : "Click to start recording"}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Speak about how you're feeling. Your voice will be analyzed for emotional cues.
                    </p>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="image" className="mt-6">
                <div className="rounded-2xl border border-border/50 bg-card p-6 space-y-4">
                  <label className="font-display font-semibold text-lg">Upload a face image</label>
                  <Input
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="rounded-xl"
                  />
                  {imagePreview && (
                    <div className="flex justify-center">
                      <img
                        src={imagePreview}
                        alt="Preview"
                        className="w-48 h-48 object-cover rounded-2xl border-2 border-primary/20"
                      />
                    </div>
                  )}
                  <Button
                    onClick={simulateAnalysis}
                    disabled={!imagePreview || analyzing}
                    className="gradient-primary text-primary-foreground rounded-full px-8"
                  >
                    {analyzing ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                    Detect Emotion
                  </Button>
                </div>
              </TabsContent>
            </Tabs>

            {/* Loading */}
            {analyzing && (
              <div className="text-center py-12 animate-fade-in">
                <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
                <p className="font-display font-semibold text-lg">Analyzing your emotion...</p>
                <p className="text-sm text-muted-foreground">Processing with AI models</p>
              </div>
            )}

            {/* Results */}
            {result && !analyzing && (
              <div className="rounded-2xl border border-primary/20 bg-card p-8 animate-scale-in">
                <h3 className="font-display font-bold text-xl mb-6 text-center">Analysis Results</h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                  <div className="text-center p-6 rounded-xl bg-muted/50">
                    <span className="text-5xl mb-3 block">{emojis[result.emotion]}</span>
                    <p className="text-sm text-muted-foreground mb-1">Detected Emotion</p>
                    <p className="font-display font-bold text-xl">{result.emotion}</p>
                  </div>
                  <div className="text-center p-6 rounded-xl bg-muted/50">
                    <span className="text-5xl mb-3 block">
                      {result.stress === "Low" ? "🟢" : result.stress === "Medium" ? "🟡" : "🔴"}
                    </span>
                    <p className="text-sm text-muted-foreground mb-1">Stress Level</p>
                    <p className={`font-display font-bold text-xl ${stressColors[result.stress]}`}>
                      {result.stress}
                    </p>
                  </div>
                  <div className="text-center p-6 rounded-xl bg-muted/50">
                    <span className="text-5xl mb-3 block">📊</span>
                    <p className="text-sm text-muted-foreground mb-1">Confidence</p>
                    <p className="font-display font-bold text-xl">{result.confidence}%</p>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row gap-4 mt-8 justify-center">
                  <Link to="/music">
                    <Button className="gradient-primary text-primary-foreground rounded-full px-8">
                      🎵 View Music Recommendations <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                  {(result.stress === "Medium" || result.stress === "High") && (
                    <Link to="/relaxation">
                      <Button variant="outline" className="rounded-full px-8 border-primary/30">
                        🧘 Relaxation Tips
                      </Button>
                    </Link>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default EmotionAnalysis;
