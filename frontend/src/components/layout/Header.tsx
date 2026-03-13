"use client";

interface Props {
  title: string;
  children?: React.ReactNode;
}

export default function Header({ title, children }: Props) {
  return (
    <div className="mb-6 flex items-center justify-between">
      <h1 className="text-2xl font-bold text-text-primary">{title}</h1>
      {children && <div className="flex items-center gap-3">{children}</div>}
    </div>
  );
}
