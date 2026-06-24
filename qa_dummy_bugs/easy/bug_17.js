--- a/qa_dummy_bugs/easy/bug_17.js
+++ b/qa_dummy_bugs/easy/bug_17.js
@@ -1,4 +1,3 @@
 // Easy Bug 17
 function init() { throw new SyntaxError("Unexpected token '<'"); }
-init();
 // Triggering CI failure 1782328139994
