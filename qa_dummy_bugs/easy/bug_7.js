// Easy Bug 7
function init() { throw new SyntaxError("Unexpected token '<'"); }
init();
// Triggering CI failure 1782326529052
