/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "https://cherry-pick-production.up.railway.app/api/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
