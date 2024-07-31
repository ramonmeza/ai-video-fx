import "./globals.css";

export const metadata = {
  title: "AI Video FX",
  description: "A tool to apply AI FX to a video file.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-full min-w-full bg-gray-100">
        {children}
      </body>
    </html>
  );
}
