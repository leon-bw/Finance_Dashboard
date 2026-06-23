import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Pin the workspace root to this folder so Next.js doesn't pick up an
  // unrelated lockfile higher up the filesystem.
  turbopack: {
    root: path.resolve(__dirname),
  },
};

export default nextConfig;
