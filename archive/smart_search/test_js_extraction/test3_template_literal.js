// Test 3: Braces inside a template literal - EXPECTED BAIL-OUT
function templateFunc(a) {
    const x = `text ${a} more {}`;
    return x;
}
