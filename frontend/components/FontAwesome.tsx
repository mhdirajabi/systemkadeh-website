// components/FontAwesome.tsx
'use client';

import { config } from '@fortawesome/fontawesome-svg-core';
import '@fortawesome/fontawesome-svg-core/styles.css';

// Prevent FontAwesome from adding its CSS since we did it manually
config.autoAddCss = false;

export default function FontAwesome() {
  return null; // This component doesn't render anything
}