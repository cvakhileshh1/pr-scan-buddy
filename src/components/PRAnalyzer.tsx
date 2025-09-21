import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { GitBranch, Code, AlertTriangle, CheckCircle, Info, FileText, Loader2 } from "lucide-react";
import { toast } from "@/hooks/use-toast";

interface CodeFeedback {
  file: string;
  line: number;
  type: 'error' | 'warning' | 'suggestion' | 'info';
  message: string;
  severity: number;
}

interface PRAnalysisResult {
  score: number;
  feedback: CodeFeedback[];
  summary: string;
  filesChanged: number;
  linesAdded: number;
  linesRemoved: number;
}

const PRAnalyzer = () => {
  const [repoUrl, setRepoUrl] = useState("");
  const [prNumber, setPrNumber] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<PRAnalysisResult | null>(null);

  const analyzePR = async () => {
    if (!repoUrl || !prNumber) {
      toast({
        title: "Missing Information",
        description: "Please provide both repository URL and PR number",
        variant: "destructive",
      });
      return;
    }

    setIsAnalyzing(true);
    
    try {
      // Mock API call - replace with actual backend endpoint
      const response = await fetch('/api/analyze-pr', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repository_url: repoUrl,
          pr_number: parseInt(prNumber),
        }),
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const result = await response.json();
      setAnalysisResult(result);
      
      toast({
        title: "Analysis Complete",
        description: `PR analyzed successfully with a score of ${result.score}/100`,
      });
    } catch (error) {
      // Mock data for demo purposes
      const mockResult: PRAnalysisResult = {
        score: 85,
        feedback: [
          {
            file: "src/auth.py",
            line: 23,
            type: "warning",
            message: "Consider using environment variables for sensitive configuration",
            severity: 3
          },
          {
            file: "src/models.py",
            line: 45,
            type: "suggestion",
            message: "Add docstring to improve code documentation",
            severity: 2
          },
          {
            file: "src/api.py",
            line: 12,
            type: "error",
            message: "Potential SQL injection vulnerability detected",
            severity: 5
          },
          {
            file: "src/utils.py",
            line: 67,
            type: "info",
            message: "Consider using type hints for better code clarity",
            severity: 1
          }
        ],
        summary: "Overall good code quality with some security concerns that need attention. The PR introduces new authentication features with proper error handling.",
        filesChanged: 4,
        linesAdded: 156,
        linesRemoved: 23
      };
      
      setAnalysisResult(mockResult);
      
      toast({
        title: "Demo Mode",
        description: "Showing mock analysis results for demonstration",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getFeedbackIcon = (type: string) => {
    switch (type) {
      case 'error':
        return <AlertTriangle className="w-4 h-4 text-destructive" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'suggestion':
        return <Info className="w-4 h-4 text-blue-500" />;
      default:
        return <CheckCircle className="w-4 h-4 text-primary" />;
    }
  };

  const getFeedbackBadgeVariant = (type: string) => {
    switch (type) {
      case 'error':
        return 'destructive';
      case 'warning':
        return 'outline';
      case 'suggestion':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-primary';
    if (score >= 70) return 'text-yellow-500';
    return 'text-destructive';
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="flex items-center justify-center gap-2 mb-4">
          <Code className="w-8 h-8 text-primary" />
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
            PR Review Agent
          </h1>
        </div>
        <p className="text-muted-foreground text-lg">
          AI-powered code review for your pull requests
        </p>
      </div>

      {/* Input Form */}
      <Card className="p-6 bg-gradient-to-br from-card to-card/50 border-border shadow-lg">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <label htmlFor="repo-url" className="text-sm font-medium">
              Repository URL
            </label>
            <Input
              id="repo-url"
              placeholder="https://github.com/username/repository"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              className="bg-background/50"
            />
          </div>
          <div className="space-y-2">
            <label htmlFor="pr-number" className="text-sm font-medium">
              Pull Request Number
            </label>
            <Input
              id="pr-number"
              placeholder="123"
              type="number"
              value={prNumber}
              onChange={(e) => setPrNumber(e.target.value)}
              className="bg-background/50"
            />
          </div>
        </div>
        <Button
          onClick={analyzePR}
          disabled={isAnalyzing}
          className="w-full mt-4 bg-primary hover:bg-primary/90"
          size="lg"
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Analyzing PR...
            </>
          ) : (
            <>
              <GitBranch className="w-4 h-4 mr-2" />
              Analyze Pull Request
            </>
          )}
        </Button>
      </Card>

      {/* Analysis Results */}
      {analysisResult && (
        <div className="space-y-6">
          {/* Summary Card */}
          <Card className="p-6 bg-gradient-to-br from-card to-card/50 border-border">
            <div className="grid gap-6 md:grid-cols-2">
              <div className="space-y-4">
                <h2 className="text-2xl font-semibold flex items-center gap-2">
                  <FileText className="w-6 h-6" />
                  Analysis Summary
                </h2>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Quality Score:</span>
                    <span className={`text-2xl font-bold ${getScoreColor(analysisResult.score)}`}>
                      {analysisResult.score}/100
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Files Changed:</span>
                    <span className="font-medium">{analysisResult.filesChanged}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Lines Added:</span>
                    <span className="font-medium text-primary">+{analysisResult.linesAdded}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Lines Removed:</span>
                    <span className="font-medium text-destructive">-{analysisResult.linesRemoved}</span>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Overview</h3>
                <Textarea
                  value={analysisResult.summary}
                  readOnly
                  className="min-h-[120px] bg-background/50 resize-none"
                />
              </div>
            </div>
          </Card>

          {/* Feedback List */}
          <Card className="p-6 bg-gradient-to-br from-card to-card/50 border-border">
            <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
              <Code className="w-6 h-6" />
              Code Feedback ({analysisResult.feedback.length} items)
            </h2>
            <div className="space-y-3">
              {analysisResult.feedback.map((item, index) => (
                <div
                  key={index}
                  className="p-4 border border-border rounded-lg bg-background/30 hover:bg-background/50 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3 flex-1">
                      {getFeedbackIcon(item.type)}
                      <div className="space-y-1 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-sm">{item.file}</span>
                          <span className="text-muted-foreground text-sm">Line {item.line}</span>
                          <Badge variant={getFeedbackBadgeVariant(item.type)} className="text-xs">
                            {item.type}
                          </Badge>
                        </div>
                        <p className="text-sm text-foreground/90">{item.message}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <div
                          key={i}
                          className={`w-2 h-2 rounded-full ${
                            i < item.severity ? 'bg-destructive' : 'bg-muted'
                          }`}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default PRAnalyzer;