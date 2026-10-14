/** @type {import('next').NextConfig} */
const nextConfig = {
  // Required for the multi-stage Docker build (frontend/Dockerfile uses .next/standalone)
  output: "standalone",

  // Allow images from Cloudinary (profile pictures)
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "res.cloudinary.com",
      },
    ],
  },
};

module.exports = nextConfig;
