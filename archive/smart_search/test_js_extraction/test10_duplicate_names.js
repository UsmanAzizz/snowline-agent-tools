// Test 10: Duplicate function names - last definition should win
function process(id) {
    return id * 1;
}

function process(id) {
    const doubled = id * 2;
    return doubled;
}

function helper() {
    return "not process";
}
