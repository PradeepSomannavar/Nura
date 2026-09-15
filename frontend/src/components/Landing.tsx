import { useEffect, useRef, useState } from "react";
import { ArrowRight } from "@phosphor-icons/react";

interface LandingProps {
  onOpenChat: () => void;
}

export function Landing({ onOpenChat }: LandingProps) {
  const [visible, setVisible] = useState(false);
  const howRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const el = howRef.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setVisible(true);
      },
      { threshold: 0.15 },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div className="page">
      <main>
        <section className="hero">
          <span className="wordmark">Nura</span>

          <div className="hero__headline">
            Clinical guide for symptoms, treatments, and care.
          </div>

          <p className="hero__sub">
            Ask Nura about symptoms, health conditions, treatment plans, drug
            interactions, or clinical care tips to receive immediate,
            source-backed answers.
          </p>

          <div className="hero__cta">
            <button
              type="button"
              className="btn btn--primary"
              onClick={onOpenChat}
            >
              <span>Ask a question</span>
              <ArrowRight size={12} weight="bold" />
            </button>
            <a className="btn btn--ghost" href="#how-it-works">
              How it works
            </a>
          </div>
        </section>

        <section
          className={`how${visible ? " visible" : ""}`}
          id="how-it-works"
          ref={howRef}
        >
          <div className="how__header">
            <h2 className="how__title">How it works</h2>
            <p className="how__lead">
              Three steps from complex medical query to cited answer.
            </p>
          </div>

          <div className="steps">
            <div className="step">
              <div className="step__num">01</div>
              <h3>Ask</h3>
              <p>
                Type your question about symptoms, conditions, treatments, or
                medications in plain language.
              </p>
            </div>

            <div className="step">
              <div className="step__num">02</div>
              <h3>Retrieve</h3>
              <p>
                Nura searches its indexed medical literature for the most
                relevant passages.
              </p>
            </div>

            <div className="step">
              <div className="step__num">03</div>
              <h3>Cited answer</h3>
              <p>
                You get a direct answer with the sources shown, so you can
                verify the evidence.
              </p>
            </div>
          </div>
        </section>
      </main>

      <footer className="footer">
        <div className="footer__inner">
          <span>&copy; Nura. Medical reference &amp; query system.</span>
          <div className="footer__links">
            <a href="#!">Privacy</a>
            <a href="#!">Disclaimer</a>
            <a href="#!">Terms</a>
          </div>
        </div>
      </footer>
    </div>
  );
}