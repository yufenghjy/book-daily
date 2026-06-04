import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import preact from '@astrojs/preact';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  output: 'static',
  integrations: [
    tailwind(),
    preact(),
    sitemap({
      filter: (page) => !page.includes('/404'),
    }),
  ],
  site: 'https://yufenghjy.github.io/book-daily',
  base: '/book-daily',
});
