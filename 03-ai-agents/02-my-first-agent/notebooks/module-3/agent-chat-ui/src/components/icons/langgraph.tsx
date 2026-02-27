export function LangGraphLogoSVG({
  className,
  width,
  height,
}: {
  width?: number;
  height?: number;
  className?: string;
}) {
  return (
    <img 
      src="/logo.png" 
      alt="Logo"
      width={width}
      height={height}
      className={className}
    />
  );
}
