// No PDF or credentials are cached for offline access.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
// Deliberately no fetch handler.
