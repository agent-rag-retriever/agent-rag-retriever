--- a/qa_dummy_bugs/hard/bug_4.js
+++ b/qa_dummy_bugs/hard/bug_4.js
@@ -2,4 +2,5 @@
 const EventEmitter = require('events');
 class MyEmitter extends EventEmitter {}
 const myEmitter = new MyEmitter();
+myEmitter.on('error', (err) => { console.error('Caught error:', err.message); });
 myEmitter.emit('error', new Error('EADDRINUSE: address already in use :::8080'));
