import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './style.css';
if ('serviceWorker' in navigator) {
 window.addEventListener('load', () => navigator.serviceWorker.register('/sw.js').catch(() => undefined));
}
const root = document.getElementById('root');
if (!root) throw new Error('App root not found');
createRoot(root).render(<React.StrictMode><App /></React.StrictMode>);
