import { useState } from "react";
import { SendHorizontal, ShieldCheck } from "lucide-react";

import { askInsureTutor, ChatResponse } from "./api";
import { CitationList } from "./components/CitationList";
import { MessageBubble } from "./components/MessageBubble";

type Message =
  | { role: "user"; content: string }
  | { role: "assistant"; content: string; response: ChatResponse };

const STARTERS = [
  "Can I skip premium payments?",
  "Is the 4% interest rate guaranteed?",
  "这份计划可以暂停缴费吗？",
  "如果现金价值不足会怎样？"
];

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(nextQuestion = question) {
    const trimmed = nextQuestion.trim();
    if (!trimmed || isLoading) {
      return;
    }

    setError(null);
    setQuestion("");
    setMessages((current) => [...current, { role: "user", content: trimmed }]);
    setIsLoading(true);

    try {
      const response = await askInsureTutor(trimmed);
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: response.answer,
          response
        }
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="workspace">
        <aside className="side-panel">
          <div className="brand-row">
            <div className="brand-mark">
              <ShieldCheck size={22} aria-hidden="true" />
            </div>
            <div>
              <h1>InsureTutor</h1>
              <p>Grounded insurance document Q&A</p>
            </div>
          </div>

          <div className="status-box">
            <span>Knowledge source</span>
            <strong>FLEXI-ULife Prime Saver</strong>
          </div>

          <div className="starter-list">
            <span>Try asking</span>
            {STARTERS.map((item) => (
              <button key={item} type="button" onClick={() => submit(item)}>
                {item}
              </button>
            ))}
          </div>
        </aside>

        <section className="chat-panel">
          <div className="messages" aria-live="polite">
            {messages.length === 0 ? (
              <div className="empty-state">
                <h2>Ask about the policy document</h2>
                <p>
                  Answers are constrained to retrieved evidence and include citations, caveats, and scope status.
                </p>
              </div>
            ) : (
              messages.map((message, index) => (
                <MessageBubble key={`${message.role}-${index}`} role={message.role}>
                  <p>{message.content}</p>
                  {message.role === "assistant" ? (
                    <>
                      {message.response.caveats.length > 0 ? (
                        <div className="caveats">
                          <strong>Important limitations</strong>
                          <ul>
                            {message.response.caveats.map((caveat) => (
                              <li key={caveat}>{caveat}</li>
                            ))}
                          </ul>
                        </div>
                      ) : null}
                      <CitationList citations={message.response.citations} />
                    </>
                  ) : null}
                </MessageBubble>
              ))
            )}
            {isLoading ? <div className="loading">Retrieving evidence...</div> : null}
          </div>

          {error ? <div className="error">{error}</div> : null}

          <form
            className="composer"
            onSubmit={(event) => {
              event.preventDefault();
              submit();
            }}
          >
            <input
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask in English or Chinese..."
              aria-label="Question"
            />
            <button type="submit" disabled={isLoading || !question.trim()} title="Send question">
              <SendHorizontal size={20} aria-hidden="true" />
            </button>
          </form>
        </section>
      </section>
    </main>
  );
}
