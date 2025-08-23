import React from "react";
type Props = React.PropsWithChildren<{ title?: string; right?: React.ReactNode }>;
export default function Card({ title, right, children }: Props) {
  return (
    <section className="card">
      {(title || right) && (
        <div className="card-head">
          <h2 className="font-semibold">{title}</h2>
          {right}
        </div>
      )}
      <div className="card-body">{children}</div>
    </section>
  );
}
