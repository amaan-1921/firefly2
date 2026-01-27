/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    serverComponentsExternalPackages: ['leaflet', 'recharts'],
  },
  output: 'standalone',
  images: {
    domains: []
  }
};

module.exports = nextConfig;
