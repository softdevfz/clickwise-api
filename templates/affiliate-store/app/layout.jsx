import "./globals.css";
import { config } from "../lib/clickwise";

export const metadata = {
  title: config.title,
  description: config.tagline,
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
