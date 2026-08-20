// Test 9: A regex literal containing a brace - EXPECTED BAIL-OUT
function regexFunc(str) {
    const re = /\{foo\}/;
    return str.match(re);
}
