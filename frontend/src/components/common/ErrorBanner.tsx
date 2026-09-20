export function ErrorBanner({ error }: { error: Error | null }) {
  if (!error) return null;
  return <div className="banner error">{error.message}</div>;
}
