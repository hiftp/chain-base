self.addEventListener('install', async event => {
  console.log('install event')
});

self.addEventListener('fetch', async event => {
  console.log('fetch event')
});