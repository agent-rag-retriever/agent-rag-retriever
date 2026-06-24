--- a/run_qa_tests.js
+++ b/run_qa_tests.js
@@ -4,9 +4,7 @@
 const BUGS = [
   {
     name: 'Infinite Recursion Bug',
-    rawLog: `RangeError: Maximum call stack size exceeded
-    at loginUser (c:\\dev\\DevOps-Autonomous-Incident-Triage-Pipeline-v2\\qa_dummy_bugs\\auth_bug.js:4:16)
-    at loginUser (c:\\dev\\DevOps-Autonomous-Incident-Triage-Pipeline-v2\\qa_dummy_bugs\\auth_bug.js:4:16)
-    at loginUser (c:\\dev\\DevOps-Autonomous-Incident-Triage-Pipeline-v2\\qa_dummy_bugs\\auth_bug.js:4:16)`
+    rawLog: `RangeError: Maximum call stack size exceeded (infinite recursion in auth_bug.js)`
   },
   {
     name: 'List Index Out of Bounds',