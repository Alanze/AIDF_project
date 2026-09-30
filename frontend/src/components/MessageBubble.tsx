import { ReactNode } from "react";

type Props = {
  role: "user" | "assistant";
  children: ReactNode;
};

export function MessageBubble({ role, children }: Props) {
  return <article className={`message ${role}`}>{children}</article>;
}
