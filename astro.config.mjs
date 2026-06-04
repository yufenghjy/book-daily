import { defineConfig } from 'astro/config';
import vercel from '@astrojs/vercel';
import tailwind from '@astrojs/tailwind';
import preact from '@astrojs/preact';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  output: 'static',
  adapter: vercel({
    webAnalytics: { enabled: false },
  }),
  integrations: [
    tailwind(),
    preact(),
    sitemap({
      filter: (page) => !page.includes('/404'),
    }),
  ],
  site: 'https://book-daily.vercel.app',
});
