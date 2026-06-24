--- a/qa_dummy_bugs/auth_bug.js
+++ b/qa_dummy_bugs/auth_bug.js
@@ -1,7 +1,7 @@
 function loginUser(req, res) {
     // BUG: Entering an endless recursive loop if session fails
     if (!req.session) {
-        return loginUser(req, res);
+        return res.status(401).send("Unauthorized: Session required");
     }
     
     return res.status(200).send("Logged in");
