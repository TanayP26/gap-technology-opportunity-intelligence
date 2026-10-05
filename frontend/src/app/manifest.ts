import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "GAP · Technology Opportunity Intelligence",
    short_name: "GAP",
    description: "Evidence-backed technology opportunity intelligence.",
    start_url: "/",
    display: "standalone",
    background_color: "#f5f7fb",
    theme_color: "#f5f7fb",
  };
}
