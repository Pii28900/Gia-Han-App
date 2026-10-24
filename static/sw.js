/* Private data is never cached by this service worker. */
self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
self.addEventListener('notificationclick',event=>{
 event.notification.close();
 event.waitUntil(self.clients.matchAll({type:'window',includeUncontrolled:true}).then(async windows=>{
  for(let client of windows)if(new URL(client.url).origin===self.location.origin){await client.navigate('/');return client.focus()}
  return self.clients.openWindow('/');
 }));
});
