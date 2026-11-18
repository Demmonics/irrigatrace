import './globals.css';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import { ThemeProvider } from '@/components/ThemeProvider';

export const metadata = {
  title: 'IrrigaTrace — Agricultural Irrigation Intelligence & Audit Observatory',
  description: 'Verifiable AI irrigation decisions with cryptographic integrity, dual Kc calculations, and human-in-the-loop audit logs.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* Anti-flash inline script */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              try {
                var saved = localStorage.getItem('irrigatrace-theme');
                var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                var theme = saved || (prefersDark ? 'dark' : 'light');
                document.documentElement.setAttribute('data-theme', theme);
                if (theme === 'dark') {
                  document.documentElement.classList.add('dark');
                } else {
                  document.documentElement.classList.remove('dark');
                }
              } catch (e) {}
            `,
          }}
        />
      </head>
      <body className="bg-page text-txt-primary min-h-screen flex flex-col antialiased selection:bg-black selection:text-white dark:selection:bg-white dark:selection:text-black">
        <ThemeProvider>
          <Navbar />
          <main className="flex-1 pt-24 pb-12 px-4 sm:px-6 max-w-7xl mx-auto w-full">
            {children}
          </main>
          <Footer />
        </ThemeProvider>
      </body>
    </html>
  );
}
