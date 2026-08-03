// Test 4: Nested braces inside template literal interpolation - EXPECTED BAIL-OUT
function nestedTemplate(obj) {
    const x = `${ {a: 1, b: 2} }`;
    return x;
}
